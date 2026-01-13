"""
LangGraph Module with Metrics Tracking
Handles LangGraph agent creation, routing, and execution with performance metrics
"""

import json
import logging
import operator
import time
from typing import TypedDict, Annotated, Sequence, Optional

from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage, ToolMessage
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode

# Try to import metrics, but don't fail if not available
try:
    from metrics import metrics
    METRICS_AVAILABLE = True
except ImportError:
    try:
        from client.metrics import metrics
        METRICS_AVAILABLE = True
    except ImportError:
        METRICS_AVAILABLE = False
        # Create dummy metrics if not available
        from collections import defaultdict
        metrics = {
            "agent_runs": 0,
            "agent_errors": 0,
            "agent_times": [],
            "llm_calls": 0,
            "llm_errors": 0,
            "llm_times": [],
            "tool_calls": defaultdict(int),
            "tool_errors": defaultdict(int),
            "tool_times": defaultdict(list),
        }


class AgentState(TypedDict):
    """State that gets passed between nodes in the graph"""
    messages: Annotated[Sequence[BaseMessage], operator.add]
    tools: dict
    llm: object
    ingest_completed: bool


def router(state):
    """Route based on what the agent decided to do"""
    last_message = state["messages"][-1]

    logger = logging.getLogger("mcp_client")
    logger.info(f"🎯 Router: Last message type = {type(last_message).__name__}")

    # Check if we just completed an ingest operation
    ingest_completed = state.get("ingest_completed", False)

    # Check if user's ORIGINAL message requested RAG (before LLM processing)
    user_message = None
    for msg in reversed(state["messages"]):
        if isinstance(msg, HumanMessage):
            user_message = msg
            break

    if user_message:
        content = user_message.content.lower()
        logger.info(f"🎯 Router: Checking user's original message: {content[:100]}")

        # Check for ingestion request - but only if not already completed
        if "ingest" in content and not ingest_completed:
            # Check if user wants to stop after one batch
            if any(stop_word in content for stop_word in ["stop", "then stop", "don't continue", "don't go on"]):
                logger.info(f"🎯 Router: User requested ONE-TIME ingest - routing there")
                return "ingest"
            else:
                logger.info(f"🎯 Router: User requested INGEST - routing there")
                return "ingest"
        elif "ingest" in content and ingest_completed:
            logger.info(f"🎯 Router: Ingest already completed - skipping to END")
            return "continue"

        # Check for EXPLICIT RAG SEARCH requests (not just "rag" in general)
        # IMPORTANT: Only route to RAG node for actual SEARCH queries
        rag_search_keywords = ["search rag", "query rag", "find in rag", "look up in rag"]
        if any(keyword in content for keyword in rag_search_keywords):
            logger.info(f"🎯 Router: User explicitly requested RAG SEARCH - routing there")
            return "rag"

    # If the AI made tool calls, go to tools node
    if isinstance(last_message, AIMessage):
        tool_calls = getattr(last_message, "tool_calls", [])
        logger.info(f"🎯 Router: Found {len(tool_calls)} tool calls")
        if tool_calls and len(tool_calls) > 0:
            logger.info(f"🎯 Router: Routing to TOOLS")
            return "tools"

    # Check for RAG-style questions (knowledge base queries)
    if isinstance(last_message, HumanMessage):
        content = last_message.content.lower()
        if not any(keyword in content for keyword in ["movie", "plex", "search", "find", "show", "media"]):
            if any(keyword in content for keyword in ["what is", "who is", "explain", "tell me about"]):
                logger.info(f"🎯 Router: Routing to RAG (knowledge query)")
                return "rag"

    # Default: continue with normal agent completion
    logger.info(f"🎯 Router: Continuing to END (normal completion)")
    return "continue"


async def rag_node(state):
    """Search RAG and provide context to answer the question"""
    logger = logging.getLogger("mcp_client")

    # Get the user's original question (most recent HumanMessage)
    user_message = None
    for msg in reversed(state["messages"]):
        if isinstance(msg, HumanMessage):
            user_message = msg
            break

    if not user_message:
        logger.error("❌ No user message found in RAG node")
        msg = AIMessage(content="Error: Could not find user's question.")
        return {"messages": state["messages"] + [msg], "llm": state.get("llm")}

    original_query = user_message.content

    # Extract the actual search terms from the query
    search_query = original_query.lower()
    for phrase in ["using the rag tool", "use the rag tool", "using rag", "use rag", "with rag",
                   "search rag for", "query rag for", "rag search for", "and my plex library",
                   "in my plex library", "from my plex library", "in my plex collection",
                   "from my plex collection"]:
        search_query = search_query.replace(phrase, "")

    search_query = search_query.strip().strip(",").strip()

    logger.info(f"🔍 RAG Node - Original query: {original_query}")
    logger.info(f"🔍 RAG Node - Cleaned search query: {search_query}")

    # Find the rag_search_tool
    tools_dict = state.get("tools", {})
    rag_search_tool = None

    available_tools = []
    for tool in tools_dict.values() if isinstance(tools_dict, dict) else tools_dict:
        if hasattr(tool, 'name'):
            available_tools.append(tool.name)
            if tool.name == "rag_search_tool":
                rag_search_tool = tool
                break

    logger.info(f"🔍 RAG Node - Available tools: {available_tools}")
    logger.info(f"🔍 RAG Node - Looking for 'rag_search_tool'")

    if not rag_search_tool:
        logger.error(f"❌ RAG search tool not found! Available: {available_tools}")
        msg = AIMessage(content=f"RAG search is not available. Available tools: {', '.join(available_tools)}")
        return {"messages": state["messages"] + [msg], "llm": state.get("llm")}

    try:
        logger.info(f"🔍 Calling rag_search_tool with query: {search_query}")

        # Track tool call timing
        tool_start = time.time()
        result = await rag_search_tool.ainvoke({"query": search_query})
        tool_duration = time.time() - tool_start

        if METRICS_AVAILABLE:
            metrics["tool_calls"]["rag_search_tool"] += 1
            metrics["tool_times"]["rag_search_tool"].append(tool_duration)
            logger.info(f"📊 Tracked rag_search_tool: {tool_duration:.2f}s")

        logger.info(f"🔍 RAG tool result type: {type(result)}")
        logger.info(f"🔍 RAG tool result (first 200 chars): {str(result)[:200]}")

        # Handle different result types
        if isinstance(result, list) and len(result) > 0:
            if hasattr(result[0], 'text'):
                logger.info("🔍 Detected actual TextContent object list")
                result_text = result[0].text
                try:
                    result = json.loads(result_text)
                    logger.info("✅ Successfully parsed JSON from TextContent object")
                except json.JSONDecodeError as e:
                    logger.error(f"❌ JSON decode error from TextContent: {e}")
                    logger.error(f"❌ TextContent string: {result_text[:500]}")
                    msg = AIMessage(content=f"Error parsing RAG results: {str(e)}")
                    return {"messages": state["messages"] + [msg], "llm": state.get("llm")}
        elif isinstance(result, str):
            if result.startswith("[TextContent("):
                logger.info("🔍 Detected TextContent string representation")

                try:
                    json_start_marker = "text='"
                    json_start_idx = result.find(json_start_marker)

                    if json_start_idx == -1:
                        raise ValueError("Could not find text=' marker")

                    json_start_idx += len(json_start_marker)

                    brace_count = 0
                    in_string = False
                    escape_next = False
                    json_end_idx = json_start_idx

                    for i in range(json_start_idx, len(result)):
                        char = result[i]

                        if escape_next:
                            escape_next = False
                            continue

                        if char == '\\':
                            escape_next = True
                            continue

                        if char == '"' and not in_string:
                            in_string = True
                        elif char == '"' and in_string:
                            in_string = False
                        elif char == '{' and not in_string:
                            brace_count += 1
                        elif char == '}' and not in_string:
                            brace_count -= 1
                            if brace_count == 0:
                                json_end_idx = i + 1
                                break

                    if json_end_idx == json_start_idx:
                        raise ValueError("Could not find end of JSON")

                    json_str = result[json_start_idx:json_end_idx]

                    import codecs
                    try:
                        json_str = codecs.decode(json_str, 'unicode_escape')
                    except Exception as decode_err:
                        logger.warning(f"⚠️ Codecs decode failed: {decode_err}, trying manual decode")
                        json_str = json_str.replace('\\n', '\n').replace('\\t', '\t').replace('\\r', '\r')
                        json_str = json_str.replace('\\\\', '\\').replace('\\"', '"')

                    logger.info(f"🔍 Extracted JSON (first 100 chars): {json_str[:100]}")

                    result = json.loads(json_str)
                    logger.info("✅ Successfully parsed JSON from TextContent string")

                except (ValueError, json.JSONDecodeError) as e:
                    logger.error(f"❌ Error parsing TextContent: {e}")
                    logger.error(f"❌ Result sample: {result[:500]}")
                    msg = AIMessage(content=f"Error parsing RAG results: {str(e)}")
                    return {"messages": state["messages"] + [msg], "llm": state.get("llm")}
            else:
                try:
                    result = json.loads(result)
                except json.JSONDecodeError as e:
                    logger.error(f"❌ JSON decode error: {e}")
                    logger.error(f"❌ Result string: {result[:500]}")
                    msg = AIMessage(content=f"Error parsing RAG results: {str(e)}")
                    return {"messages": state["messages"] + [msg], "llm": state.get("llm")}

        chunks = []
        if isinstance(result, dict):
            results_list = result.get("results", [])
            chunks = [item.get("text", "") for item in results_list if isinstance(item, dict)]
            logger.info(f"✅ Extracted {len(chunks)} chunks from RAG results")

            for i, chunk in enumerate(chunks[:3]):
                logger.info(f"📄 Chunk {i+1} preview: {chunk[:150]}...")

        if not chunks:
            logger.warning("⚠️ No chunks found in RAG results")
            msg = AIMessage(content="I couldn't find any relevant information in the knowledge base for your query.")
            return {"messages": state["messages"] + [msg], "llm": state.get("llm")}

        # Take top 3 chunks
        context = "\n\n---\n\n".join(chunks[:3])
        logger.info(f"📄 Using top 3 chunks as context")

        # DIAGNOSTIC: Log what we're sending
        logger.info("=" * 80)
        logger.info("🔍 CONTEXT BEING SENT TO LLM:")
        logger.info("=" * 80)
        logger.info(context[:1500])
        if len(context) > 1500:
            logger.info(f"... (truncated, total: {len(context)} chars)")
        logger.info("=" * 80)

        # Create fresh conversation with ONLY the context
        augmented_messages = [
            SystemMessage(content=f"""You are answering a question about movies in a user's Plex library.

The library has already been searched. Here are the ACTUAL RESULTS:

{context}

Your job: Answer the question using ONLY the movies listed above.

CORRECT response format:
"Based on your Plex library, here are movies that match:

1. [Title from results above] ([Year]) - [Brief description from results]
2. [Title from results above] ([Year]) - [Brief description from results]

etc."

WRONG responses:
- Suggesting to use tools (the search already happened!)
- Mentioning movies not in the results above
- Saying "let's search" or "we can use"

The movies shown above ARE the search results. Just present them."""),
            user_message
        ]

        llm = state.get("llm")
        logger.info(f"🔍 LLM from state: type={type(llm)}, value={llm}")

        if not llm or not hasattr(llm, 'ainvoke'):
            logger.warning("⚠️ LLM not provided or invalid in state, creating new instance")
            from langchain_ollama import ChatOllama
            llm = ChatOllama(model="llama3.1:8b", temperature=0)
            logger.info("📝 Created new LLM instance for RAG")

        logger.info("🧠 Calling LLM with RAG context")

        # Track LLM call for RAG
        llm_start = time.time()
        response = await llm.ainvoke(augmented_messages)
        llm_duration = time.time() - llm_start

        if METRICS_AVAILABLE:
            metrics["llm_calls"] += 1
            metrics["llm_times"].append(llm_duration)

        logger.info(f"✅ RAG response generated: {response.content[:100]}...")

        return {"messages": state["messages"] + [response], "llm": state.get("llm")}

    except Exception as e:
        logger.error(f"❌ Error in RAG node: {e}")
        if METRICS_AVAILABLE:
            metrics["tool_errors"]["rag_search_tool"] += 1
        msg = AIMessage(content=f"Error searching knowledge base: {str(e)}")
        return {"messages": state["messages"] + [msg], "llm": state.get("llm")}


def filter_tools_by_intent(user_message: str, all_tools: list) -> list:
    """Filter tools based on user intent"""
    user_message_lower = user_message.lower()
    logger = logging.getLogger("mcp_client")

    # PRIORITY: Check for EXPLICIT tool name mentions
    # If user explicitly names a tool, assume they know what they want
    for tool in all_tools:
        tool_name_lower = tool.name.lower()
        # Check for exact tool name or "use X tool" patterns
        if (tool_name_lower in user_message_lower or
                f"use {tool_name_lower}" in user_message_lower or
                f"call {tool_name_lower}" in user_message_lower or
                f"using {tool_name_lower}" in user_message_lower):
            logger.info(f"🎯 User explicitly requested {tool.name}")
            return [tool]  # Return ONLY that tool

    # LLM-ONLY DETECTION
    # Check if user explicitly wants LLM-only response without tools
    llm_only_keywords = [
        # Explicit LLM/AI requests
        "using llm", "use llm", "using the llm", "llm only", "just llm", "only llm", "only the llm",
        "using ai", "use ai", "ai only", "just ai", "only ai",
        "using claude", "use claude", "claude only", "just claude",
        "think like an ai", "think like a human", "use your knowledge",
        "from your training", "what do you know", "in your opinion",

        # Tool restrictions
        "don't use tools", "no tools", "without tools", "skip tools",
        "don't call tools", "without calling tools", "no tool calls",
        "don't use any tools", "do not use tools",

        # Specific tool restrictions
        "don't search", "no search", "without searching", "skip search",
        "don't call rag", "no rag", "without rag", "skip rag",
        "don't use plex", "no plex", "without plex", "skip plex",
        "don't check", "no checking", "without checking",
        "don't look up", "no looking up", "without looking up",

        # General knowledge requests
        "just tell me", "just explain", "just answer", "simply tell me",
        "off the top of your head", "from memory", "what you know already",
        "based on your knowledge", "using your knowledge",

        # Conversational/opinion requests
        "what's your take", "what's your opinion", "your thoughts on",
        "how would you", "what would you", "in your view", "from your perspective"
    ]

    if any(keyword in user_message_lower for keyword in llm_only_keywords):
        logger.info("🧠 Detected LLM-ONLY intent - NO TOOLS will be provided")
        return []  # Empty list = no tools = LLM-only response

    # Knowledge Base / Note Adding (check BEFORE to-do)
    kb_add_keywords = [
        # Direct commands
        "add to knowledge", "add to my knowledge", "add to kb", "add to my kb",
        "save to knowledge", "save to my knowledge", "save to kb", "save to my kb",
        "store in knowledge", "store in my knowledge", "store in kb",

        # Note-taking language
        "remember this", "save this", "make a note", "write down",
        "note that", "keep track of", "record this", "jot down",
        "save note", "add note", "create note", "add entry", "create entry",

        # URL/content specific
        "add this url", "save this url", "add this link", "save this link",
        "add this page", "save this page", "add this site", "save this site",
        "add https://", "save https://", "store https://",

        # Document/text storage
        "save this information", "store this information",
        "add this to my notes", "save this to my notes",
        "remember that", "don't forget that"
    ]

    if any(keyword in user_message_lower for keyword in kb_add_keywords):
        logger.info("🎯 Detected KNOWLEDGE BASE ADD intent")
        return [t for t in all_tools if t.name in [
            "rag_add_tool",  # RAG ingestion
            "add_entry",  # Direct KB add
            "list_entries",  # To verify after adding
            "get_entry"  # To check what was added
        ]]

    # Knowledge Base / Note Searching
    kb_search_keywords = [
        "search my notes", "search my knowledge", "search kb", "search my kb",
        "what do i know about", "what did i save about", "what have i stored about",
        "find in my notes", "find in my knowledge", "look up in notes",
        "what did i write about", "what did i record about",
        "search entries", "find entries", "search entry", "find entry"
    ]

    if any(keyword in user_message_lower for keyword in kb_search_keywords):
        logger.info("🎯 Detected KNOWLEDGE BASE SEARCH intent")
        return [t for t in all_tools if t.name in [
            "rag_search_tool", "search_entries", "search_semantic",
            "search_by_tag", "get_entry", "list_entries"
        ]]

    # Check for EXPLICIT tool name mentions (user debugging)
    # If user explicitly names a tool, assume they know what they want
    explicit_tool_mentions = [
        "using the", "use the", "call the", "with the", "using tool",
        "use tool", "call tool"
    ]

    if any(phrase in user_message_lower for phrase in explicit_tool_mentions):
        # Extract the tool name they mentioned
        for tool in all_tools:
            if tool.name.lower() in user_message_lower:
                logger.info(f"🎯 User explicitly requested {tool.name}")
                return [tool]  # Return ONLY that tool

    # To-do intent (check BEFORE note intent)
    todo_keywords = [
        # Marking complete/done
        "mark", "complete", "finish", "done", "finished", "completed",
        "mark as complete", "mark as done", "mark complete", "mark done",
        "set to complete", "set to done", "set as complete", "set as done",
        "check off", "checked off", "cross off",

        # Todo/task general terms
        "todo", "task", "to-do", "to do",
        "todo list", "task list", "my todos", "my tasks",

        # Adding
        "add to my", "add to", "remind me", "remind me to",
        "i need to", "don't forget", "don't forget to",
        "create a todo", "create a task", "create todo", "create task",
        "new todo", "new task", "add todo", "add task",
        "make a todo", "make a task",

        # Viewing/Listing
        "show my todos", "show my tasks", "show todos", "show tasks",
        "list my todos", "list my tasks", "list todos", "list tasks",
        "what do i need to do", "what's on my todo", "what's in my todo",
        "check my todos", "check my tasks", "view my todos", "view my tasks",
        "see my todos", "see my tasks", "display todos", "display tasks",
        "get my todos", "get my tasks",

        # Status-specific
        "incomplete todos", "incomplete tasks", "non complete todos", "non complete tasks",
        "unfinished todos", "unfinished tasks", "open todos", "open tasks",
        "pending todos", "pending tasks", "active todos", "active tasks",
        "outstanding todos", "outstanding tasks",

        # Searching
        "find todos", "find tasks", "search todos", "search tasks",
        "todos about", "tasks about", "todos for", "tasks for",
        "todos containing", "tasks containing", "look for todo", "look for task",

        # Updating/Modifying
        "update todo", "update task", "change todo", "change task",
        "modify todo", "modify task", "edit todo", "edit task",
        "update my todo", "update my task", "change my todo", "change my task",

        # Deleting/Removing
        "delete todo", "delete task", "remove todo", "remove task",
        "clear todos", "clear tasks", "clear all todos", "clear all tasks",
        "delete all todos", "delete all tasks", "remove all todos", "remove all tasks",

        # Referencing by number/position
        "mark 1", "mark #", "mark item", "mark number",
        "complete 1", "complete #", "complete item", "complete number",
        "task 1", "task #", "todo 1", "todo #",
        "first todo", "first task", "second todo", "second task",
        "next todo", "next task",

        # Action-oriented phrases
        "mark brekkie", "complete brekkie", "finish brekkie",  # Example from your logs
        "i did", "i finished", "i completed", "i'm done with",
        "finished with", "done with", "completed the",

        # Status checks
        "what's left", "what remains", "what's remaining",
        "what haven't i done", "what's not done", "what's incomplete",
    ]

    if any(keyword in user_message_lower for keyword in todo_keywords):
        logger.info("🎯 Detected TODO intent")
        return [t for t in all_tools if t.name in [
            "add_todo_item", "list_todo_items", "search_todo_items",
            "update_todo_item", "delete_todo_item", "delete_all_todo_items"
        ]]

    # Todo/task keywords - COMPREHENSIVE LIST
    todo_keywords = [
        # Adding
        "add to my todo", "add to my tasks", "remind me to", "i need to", "don't forget",
        "create a todo", "create a task", "new todo", "new task",

        # Viewing/Listing
        "todo list", "my todos", "my tasks", "task list", "what do i need to do",
        "show my todos", "list my todos", "show my tasks", "what's in my todo",
        "what's on my todo", "check my todos", "view my todos", "see my todos",
        "display todos", "display tasks", "show tasks", "list tasks",

        # Status-specific
        "incomplete todos", "non complete todos", "unfinished todos", "open todos",
        "pending todos", "active todos", "incomplete tasks", "unfinished tasks",
        "open tasks", "pending tasks", "active tasks",

        # Searching
        "find todos", "search todos", "find tasks", "search tasks",
        "todos about", "tasks about", "todos for", "tasks for",

        # Updating
        "update todo", "update task", "change todo", "modify todo",
        "mark as complete", "mark as done", "complete todo", "finish todo",

        # Deleting
        "delete todo", "remove todo", "delete task", "remove task",
        "clear todos", "clear tasks"
    ]

    if any(keyword in user_message_lower for keyword in todo_keywords):
        logger.info("🎯 Detected TODO intent")
        return [t for t in all_tools if t.name in [
            "add_todo_item", "list_todo_items", "search_todo_items",
            "update_todo_item", "delete_todo_item", "delete_all_todo_items"
        ]]

    # Note/memory keywords
    note_keywords = [
        "remember", "save this", "make a note", "write down", "store this",
        "note that", "keep track of", "record this", "jot down",
        "save note", "add note", "create note"
    ]

    if any(keyword in user_message_lower for keyword in note_keywords):
        logger.info("🎯 Detected MEMORY/NOTE intent")
        return [t for t in all_tools if t.name in [
            "rag_add_tool", "add_entry", "list_entries", "get_entry", "search_entries"
        ]]

    # RAG diagnostic keywords (add BEFORE rag_search_keywords)
    rag_diagnostic_keywords = [
        "diagnose rag", "rag diagnose", "check rag", "rag status",
        "missing subtitles", "incomplete rag", "rag problems",
        "what's missing", "what's not ingested", "rag health"
    ]

    if any(keyword in user_message_lower for keyword in rag_diagnostic_keywords):
        logger.info("🎯 Detected RAG DIAGNOSTIC intent")
        return [t for t in all_tools if t.name in [
            "rag_diagnose_tool",
            "semantic_media_search_text",  # To look up specific items
            "rag_search_tool"  # To verify what's in RAG
        ]]

    # RAG status keywords
    rag_status_keywords = [
        "rag status", "check rag", "how many in rag", "what's in rag",
        "rag contents", "rag count", "rag size", "rag info"
    ]

    if any(keyword in user_message_lower for keyword in rag_status_keywords):
        logger.info("🎯 Detected RAG STATUS intent")
        return [t for t in all_tools if t.name in [
            "rag_status_tool",
            "rag_diagnose_tool"
        ]]

    # RAG search keywords
    rag_search_keywords = [
        "using the rag tool", "search my notes", "what do i know about",
        "find information", "search for information", "look up in notes",
        "what did i save about", "search notes", "find in notes"
    ]

    if any(keyword in user_message_lower for keyword in rag_search_keywords):
        logger.info("🎯 Detected RAG SEARCH intent")
        return [t for t in all_tools if t.name in [
            "rag_search_tool", "search_entries", "search_semantic", "search_by_tag"
        ]]

    # Plex ingestion keywords
    plex_ingest_keywords = [
        "ingest", "ingest plex", "ingest from plex", "ingest next",
        "add plex to rag", "ingest batch", "process plex", "load plex"
    ]

    if any(keyword in user_message_lower for keyword in plex_ingest_keywords):
        logger.info("🎯 Detected PLEX INGEST intent")
        return [t for t in all_tools if t.name in [
            "plex_ingest_batch",
            "rag_search_tool",  # To verify after ingestion
            "semantic_media_search_text"  # To find what was ingested
        ]]

    # Media/Plex keywords
    media_keywords = [
        "find movie", "find movies", "search plex", "what movies", "show me",
        "movies about", "films about", "search for movie", "look for movie",
        "search media", "find film", "find films"
    ]

    if any(keyword in user_message_lower for keyword in media_keywords):
        logger.info("🎯 Detected MEDIA search intent")
        return [t for t in all_tools if t.name in [
            "semantic_media_search_text", "scene_locator_tool", "find_scene_by_title"
        ]]

    # Weather keywords
    if any(keyword in user_message_lower for keyword in ["weather", "temperature", "forecast"]):
        logger.info("🎯 Detected WEATHER intent")
        return [t for t in all_tools if t.name in [
            "get_weather_tool", "get_location_tool"
        ]]

    # System/hardware keywords
    if any(keyword in user_message_lower for keyword in [
        "system", "hardware", "cpu", "gpu", "memory", "processes", "specs"
    ]):
        logger.info("🎯 Detected SYSTEM intent")
        return [t for t in all_tools if t.name in [
            "get_hardware_specs_tool", "get_system_info", "list_system_processes", "terminate_process"
        ]]

    # Default: return all tools but log warning
    logger.warning(f"🎯 No specific intent detected for: '{user_message}' - using all {len(all_tools)} tools")
    return all_tools

def create_langgraph_agent(llm_with_tools, tools):
    """Create and compile the LangGraph agent"""
    logger = logging.getLogger("mcp_client")

    # IMPORTANT: Store the base LLM (without tools) for dynamic binding
    # llm_with_tools is a RunnableBinding, we need the underlying LLM
    base_llm = llm_with_tools.bound if hasattr(llm_with_tools, 'bound') else llm_with_tools

    async def call_model(state: AgentState):
        messages = state["messages"]

        # Get user's original message for tool filtering
        user_message = None
        for msg in reversed(messages):
            if isinstance(msg, HumanMessage):
                user_message = msg.content
                break

                # Look for recent list_todo_items calls
            todo_context = None
            for msg in reversed(messages[-10:]):  # Check last 10 messages
                if isinstance(msg, ToolMessage) and hasattr(msg, 'name'):
                    if msg.name == "list_todo_items":
                        # Extract todo items from result
                        try:
                            import json
                            content = msg.content
                            if isinstance(content, list) and hasattr(content[0], 'text'):
                                content = content[0].text

                            todos = json.loads(content)
                            if todos:
                                todo_context = "\n".join([
                                    f"- '{todo['title']}' (id: {todo['id']}, status: {todo.get('status', 'unknown')})"
                                    for todo in todos[:5]  # Top 5
                                ])
                                logger.info(f"📋 Found recent todo list context")
                                break
                        except Exception as e:
                            logger.warning(f"⚠️ Couldn't extract todo context: {e}")

            # If we have to-do context and user is asking to update something
            if todo_context and user_message:
                user_lower = user_message.lower()
                if any(word in user_lower for word in ['mark', 'complete', 'update', 'finish']):
                    # Add context message
                    context_msg = SystemMessage(content=f"""RECENT TODO ITEMS:
               {todo_context}

               When the user refers to a todo by name or number, use the ID shown above.""")
                    messages = [messages[0]] + [context_msg] + messages[1:]  # Insert after system prompt
                    logger.info("📋 Added todo context to LLM")

        # Filter tools based on user intent
        llm_to_use = llm_with_tools
        is_llm_only_mode = False

        if user_message:
            # Get all available tools from state
            all_tools = list(state.get("tools", {}).values())
            filtered_tools = filter_tools_by_intent(user_message, all_tools)

            # Check if LLM-only mode (empty tool list)
            if len(filtered_tools) == 0:
                logger.info(f"🧠 LLM-ONLY MODE: Using base LLM without any tools")
                llm_to_use = base_llm
                is_llm_only_mode = True

                # CRITICAL: Add a system message to prevent tool mentions
                # Remove any existing system messages and add LLM-only instruction
                filtered_messages = [m for m in messages if not isinstance(m, SystemMessage)]
                llm_only_system = SystemMessage(content="""You are a helpful AI assistant. 

    IMPORTANT: You do NOT have access to any tools, functions, or external data sources. 
    Do NOT mention calling tools, searching, or looking things up.
    Answer questions directly using ONLY your training knowledge.
    If you don't know something, simply say you don't know.

    Be concise and helpful.""")
                messages = [llm_only_system] + filtered_messages

            else:
                tool_names = [t.name for t in filtered_tools]
                logger.info(f"🎯 Filtered to {len(filtered_tools)} relevant tools: {tool_names}")
                llm_to_use = base_llm.bind_tools(filtered_tools)
        else:
            llm_to_use = llm_with_tools

        logger.info(f"🧠 Calling LLM with {len(messages)} messages")

        start_time = time.time()
        try:
            response = await llm_to_use.ainvoke(messages)
            duration = time.time() - start_time

            # Track LLM metrics
            if METRICS_AVAILABLE:
                metrics["llm_calls"] += 1
                metrics["llm_times"].append(duration)

            tool_calls = getattr(response, "tool_calls", [])
            logger.info(f"🔧 LLM returned {len(tool_calls)} tool calls")

            # CRITICAL: Only parse text for tool calls if NOT in LLM-only mode
            if not is_llm_only_mode and len(tool_calls) == 0 and response.content:
                import re
                import json as json_module

                content = response.content.strip()

                try:
                    parsed = json_module.loads(content)
                    if isinstance(parsed, dict) and parsed.get("name"):
                        tool_name = parsed["name"]
                        args = parsed.get("arguments", {})
                        if isinstance(args, str):
                            try:
                                args = json_module.loads(args)
                            except:
                                args = {}

                        logger.info(f"🔧 Parsed JSON tool call: {tool_name}({args})")
                        response.tool_calls = [{
                            "name": tool_name,
                            "args": args,
                            "id": "manual_call_1",
                            "type": "tool_call"
                        }]
                except (json_module.JSONDecodeError, ValueError):
                    match = re.search(r'(\w+)\((.*?)\)', content.replace('\n', '').replace('`', ''))
                    if match:
                        tool_name = match.group(1)
                        args_str = match.group(2).strip()

                        args = {}
                        if args_str:
                            for arg_match in re.finditer(r'(\w+)\s*=\s*(["\']?)([^,\)]+)\2', args_str):
                                key = arg_match.group(1)
                                value = arg_match.group(3).strip().strip('"\'')
                                try:
                                    value = int(value)
                                except:
                                    pass
                                args[key] = value

                        logger.info(f"🔧 Parsed function call: {tool_name}({args})")
                        response.tool_calls = [{
                            "name": tool_name,
                            "args": args,
                            "id": "manual_call_1",
                            "type": "tool_call"
                        }]

            if hasattr(response, 'tool_calls') and response.tool_calls:
                for tc in response.tool_calls:
                    logger.info(f"🔧   Tool: {tc.get('name', 'unknown')}, Args: {tc.get('args', {})}")
            else:
                content = response.content if hasattr(response, 'content') else str(response)
                logger.info(f"🔧 No tool calls. Full response: {content}")

            if hasattr(response, 'content'):
                if not response.content or not response.content.strip():
                    logger.info("⚠️ LLM returned empty content (may have tool_calls)")

            return {
                "messages": messages + [response],
                "tools": state.get("tools", {}),
                "llm": state.get("llm"),
                "ingest_completed": state.get("ingest_completed", False),
            }
        except Exception as e:
            duration = time.time() - start_time
            if METRICS_AVAILABLE:
                metrics["llm_errors"] += 1
                metrics["llm_times"].append(duration)

            logger.error(f"❌ Error in call_model: {str(e)}")
            return {
                "messages": messages + [AIMessage(content=f"Error: {str(e)}")],
                "tools": state.get("tools", {}),
                "llm": state.get("llm"),
                "ingest_completed": state.get("ingest_completed", False),
            }

    async def ingest_node(state: AgentState):
        tools_dict = state.get("tools", {})
        ingest_tool = None

        for tool in tools_dict.values() if isinstance(tools_dict, dict) else tools_dict:
            if hasattr(tool, 'name') and tool.name == "plex_ingest_batch":
                ingest_tool = tool
                break

        if not ingest_tool:
            msg = AIMessage(content="Ingestion tool not available.")
            return {
                "messages": state["messages"] + [msg],
                "tools": state.get("tools", {}),
                "llm": state.get("llm"),
                "ingest_completed": state.get("ingest_completed", False),
            }

        try:
            logger.info("📥 Starting ingest operation...")
            limit = 5
            rescan_no_subtitles = False
            messages = state["messages"]

            # Extract parameters from LLM tool call
            for msg in reversed(messages):
                if isinstance(msg, AIMessage) and hasattr(msg, 'tool_calls') and msg.tool_calls:
                    for tool_call in msg.tool_calls:
                        if tool_call.get('name') == 'plex_ingest_batch':
                            args = tool_call.get('args', {})
                            limit = args.get('limit', 5)
                            rescan_no_subtitles = args.get('rescan_no_subtitles', False)
                            logger.info(f"📥 Using limit={limit}, rescan={rescan_no_subtitles} from LLM tool call")
                            break
                    break

            logger.info(f"📥 Starting ingest operation with limit={limit}, rescan={rescan_no_subtitles}...")
            result = await ingest_tool.ainvoke({"limit": limit, "rescan_no_subtitles": rescan_no_subtitles})

            logger.info(f"🔍 Raw result type: {type(result)}")
            logger.info(f"🔍 Raw result: {result}")

            if isinstance(result, list) and len(result) > 0:
                if hasattr(result[0], 'text'):
                    logger.info("🔍 Detected TextContent object in list")
                    result = result[0].text
                    logger.info(f"🔍 Extracted text from object, length: {len(result)}")

            if isinstance(result, str) and result.startswith('[TextContent('):
                logger.info("🔍 Detected TextContent string, extracting...")
                import re

                start_marker = "text='"
                start_idx = result.find(start_marker)

                if start_idx != -1:
                    start_idx += len(start_marker)

                    end_markers = ["', annotations=", "', type="]
                    end_idx = -1

                    for marker in end_markers:
                        idx = result.find(marker, start_idx)
                        if idx != -1:
                            if end_idx == -1 or idx < end_idx:
                                end_idx = idx

                    if end_idx != -1:
                        json_str = result[start_idx:end_idx]

                        import codecs
                        try:
                            json_str = codecs.decode(json_str, 'unicode_escape')
                        except Exception as decode_err:
                            logger.warning(f"⚠️ Codecs decode failed: {decode_err}, trying manual decode")
                            json_str = json_str.replace('\\n', '\n').replace('\\t', '\t')
                            json_str = json_str.replace('\\\\', '\\').replace("\\'", "'").replace('\\"', '"')

                        result = json_str
                        logger.info(f"🔍 Extracted text, length: {len(result)}")

            if isinstance(result, str):
                try:
                    result = json.loads(result)
                    logger.info(f"✅ Successfully parsed JSON result")
                except json.JSONDecodeError as e:
                    logger.error(f"❌ JSON decode error: {e}")
                    msg = AIMessage(
                        content=f"Error: Could not parse ingestion result. Check logs for details.")
                    return {
                        "messages": state["messages"] + [msg],
                        "tools": state.get("tools", {}),
                        "llm": state.get("llm"),
                        "ingest_completed": True,
                    }

            if isinstance(result, dict) and "error" in result:
                msg = AIMessage(content=f"Ingestion error: {result['error']}")
            else:
                ingested = result.get('ingested', [])
                skipped = result.get('skipped', [])
                stats = result.get('stats', {})

                if ingested:
                    # Build detailed list of ingested items
                    items_list = []
                    for item in ingested:
                        items_list.append(
                            f"✅ **{item['title']}**\n"
                            f"   • ID: {item['id']}\n"
                            f"   • Chunks: {item['subtitle_chunks']}\n"
                            f"   • Words: ~{item['subtitle_word_count']}"
                        )

                    message_parts = [
                        f"📥 **Successfully Ingested {len(ingested)} Items:**\n",
                        "\n\n".join(items_list)
                    ]
                else:
                    message_parts = ["📥 **Ingestion Complete - No New Items Added**"]

                # Show skipped items grouped by reason
                if skipped:
                    already_ingested = [s for s in skipped if "already ingested" in s['reason'].lower()]
                    no_subtitles = [s for s in skipped if "no subtitles" in s['reason'].lower()]

                    if already_ingested:
                        message_parts.append(
                            f"\n\n⏭️  **Already Ingested ({len(already_ingested)} items):**\n" +
                            "\n".join(f"   • {s['title']}" for s in already_ingested[:3]) +
                            (f"\n   • ... and {len(already_ingested) - 3} more" if len(already_ingested) > 3 else "")
                        )

                    if no_subtitles:
                        message_parts.append(
                            f"\n\n⚠️  **Missing Subtitles ({len(no_subtitles)} items):**\n" +
                            "\n".join(f"   • {s['title']}" for s in no_subtitles[:3]) +
                            (f"\n   • ... and {len(no_subtitles) - 3} more" if len(no_subtitles) > 3 else "")
                        )

                # Add clear statistics
                message_parts.extend([
                    f"\n\n📊 **Library Statistics:**",
                    f"• Total items in Plex: **{stats.get('total_items', 0)}**",
                    f"• Successfully in RAG: **{stats.get('successfully_ingested', 0)}** items with subtitles",
                    f"• Missing subtitles: **{stats.get('missing_subtitles', 0)}** items",
                    f"• Not yet processed: **{stats.get('remaining_unprocessed', 0)}** items",
                    f"\n📝 **This Batch:**",
                    f"• Items checked: {result.get('items_checked', 0)}",
                    f"• New items processed: {result.get('items_processed', 0)}",
                    f"\n💡 Use `rescan_no_subtitles=True` to re-check items that were missing subtitles."
                ])

                msg = AIMessage(content="\n".join(message_parts))

            logger.info("✅ Ingest operation completed successfully")

        except Exception as e:
            logger.error(f"❌ Error in ingest_node: {e}")
            import traceback
            traceback.print_exc()
            msg = AIMessage(content=f"Ingestion failed: {str(e)}")

        return {
            "messages": state["messages"] + [msg],
            "tools": state.get("tools", {}),
            "llm": state.get("llm"),
            "ingest_completed": True,
        }

    workflow = StateGraph(AgentState)

    workflow.add_node("agent", call_model)
    workflow.add_node("tools", ToolNode(tools))
    workflow.add_node("rag", rag_node)
    workflow.add_node("ingest", ingest_node)

    workflow.set_entry_point("agent")

    workflow.add_conditional_edges(
        "agent",
        router,
        {
            "tools": "tools",
            "rag": "rag",
            "ingest": "ingest",
            "continue": END
        }
    )

    workflow.add_edge("tools", "agent")
    workflow.add_edge("ingest", END)
    workflow.add_edge("rag", END)

    app = workflow.compile()
    logger.info("✅ LangGraph agent compiled successfully")

    return app


async def run_agent(agent, conversation_state, user_message, logger, tools, system_prompt, llm=None, max_history=20):
    """Execute the agent with the given user message and track metrics"""

    start_time = time.time()

    try:
        if METRICS_AVAILABLE:
            metrics["agent_runs"] += 1

        conversation_state["loop_count"] += 1

        if conversation_state["loop_count"] >= 5:
            logger.error("⚠️ Loop detected — stopping early after 5 iterations.")
            if METRICS_AVAILABLE:
                metrics["agent_errors"] += 1
                duration = time.time() - start_time
                metrics["agent_times"].append(duration)

            error_msg = AIMessage(
                content=(
                    "I detected that this request was causing repeated reasoning loops. "
                    "I'm stopping early to avoid getting stuck. "
                    "Try rephrasing your request or simplifying what you're asking for."
                )
            )
            conversation_state["messages"].append(error_msg)
            conversation_state["loop_count"] = 0
            return {"messages": conversation_state["messages"]}

        # Initialize with system message if needed
        if not conversation_state["messages"]:
            conversation_state["messages"].append(
                SystemMessage(content=system_prompt)
            )

        # Add the new user message
        conversation_state["messages"].append(
            HumanMessage(content=user_message)
        )

        # Trim history BEFORE invoking agent
        conversation_state["messages"] = conversation_state["messages"][-max_history:]

        # Ensure system message is at the start after trimming
        if not isinstance(conversation_state["messages"][0], SystemMessage):
            conversation_state["messages"].insert(0, SystemMessage(content=system_prompt))

        logger.info(f"🧠 Starting agent with {len(conversation_state['messages'])} messages")

        tool_registry = {tool.name: tool for tool in tools}

        # Invoke the agent
        result = await agent.ainvoke({
            "messages": conversation_state["messages"],
            "tools": tool_registry,
            "llm": llm,
            "ingest_completed": False
        })

        new_messages = result["messages"][len(conversation_state["messages"]):]
        logger.info(f"📨 Agent added {len(new_messages)} new messages")
        conversation_state["messages"].extend(new_messages)

        # Track tool calls from AIMessages with tool_calls
        if METRICS_AVAILABLE:
            from langchain_core.messages import ToolMessage
            tool_calls_seen = set()

            for msg in new_messages:
                # Track from ToolMessage to avoid double counting
                if isinstance(msg, ToolMessage):
                    tool_name = getattr(msg, 'name', None)
                    tool_id = getattr(msg, 'tool_call_id', None)

                    if tool_name and tool_id and tool_id not in tool_calls_seen:
                        tool_calls_seen.add(tool_id)
                        metrics["tool_calls"][tool_name] += 1
                        logger.info(f"📊 Tracked tool: {tool_name}")

        # Reset loop count
        conversation_state["loop_count"] = 0

        # Track successful agent run
        if METRICS_AVAILABLE:
            duration = time.time() - start_time
            metrics["agent_times"].append(duration)
            logger.info(f"✅ Agent run completed in {duration:.2f}s")

        # Debug: Log final state
        logger.info(f"📨 Final conversation has {len(conversation_state['messages'])} messages")
        for i, msg in enumerate(conversation_state['messages'][-5:]):
            msg_type = type(msg).__name__
            content_preview = msg.content[:100] if hasattr(msg, 'content') else str(msg)[:100]
            logger.info(f"  [-{5 - i}] {msg_type}: {content_preview}")

        return {"messages": conversation_state["messages"]}

    except Exception as e:
        if METRICS_AVAILABLE:
            metrics["agent_errors"] += 1
            duration = time.time() - start_time
            metrics["agent_times"].append(duration)

        if "GraphRecursionError" in str(e):
            logger.error("❌ Recursion limit reached — stopping agent loop safely.")
            error_msg = AIMessage(
                content=(
                    "I ran into a recursion limit while processing your request. "
                    "This usually means the model kept looping instead of producing a final answer. "
                    "Try rephrasing your request or simplifying what you're asking for."
                )
            )
            conversation_state["messages"].append(error_msg)
            return {"messages": conversation_state["messages"]}

        logger.exception(f"❌ Unexpected error in agent execution")
        error_text = getattr(e, "args", [str(e)])[0]
        error_msg = AIMessage(
            content=f"An error occurred while running the agent:\n\n{error_text}"
        )
        conversation_state["messages"].append(error_msg)
        return {"messages": conversation_state["messages"]}