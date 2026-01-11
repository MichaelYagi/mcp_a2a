"""
LangGraph Module with Metrics Tracking
Handles LangGraph agent creation, routing, and execution with performance metrics
"""

import json
import logging
import operator
import time
from typing import TypedDict, Annotated, Sequence, Optional

from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
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

        # Check for EXPLICIT RAG requests (highest priority)
        if any(keyword in content for keyword in
               ["using rag", "use rag", "rag tool", "with rag", "search rag", "query rag"]):
            logger.info(f"🎯 Router: User explicitly requested RAG - routing there")
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
                   "search rag for", "query rag for", "rag search for"]:
        search_query = search_query.replace(phrase, "")

    search_query = search_query.strip().strip(",").strip()

    logger.info(f"🔍 RAG Node - Original query: {original_query}")
    logger.info(f"🔍 RAG Node - Cleaned search query: {search_query}")

    # Find the rag_search_tool
    tools_dict = state.get("tools", {})
    rag_search_tool = None

    for tool in tools_dict.values() if isinstance(tools_dict, dict) else tools_dict:
        if hasattr(tool, 'name') and tool.name == "rag_search_tool":
            rag_search_tool = tool
            break

    if not rag_search_tool:
        logger.error(f"❌ RAG search tool not found!")
        msg = AIMessage(content=f"RAG search is not available.")
        return {"messages": state["messages"] + [msg], "llm": state.get("llm")}

    try:
        logger.info(f"🔍 Calling rag_search_tool with query: {search_query}")
        result = await rag_search_tool.ainvoke({"query": search_query})

        # Process result and create response
        msg = AIMessage(content=f"RAG search completed: {str(result)[:200]}")
        return {"messages": state["messages"] + [msg], "llm": state.get("llm")}

    except Exception as e:
        logger.error(f"❌ Error in rag_node: {e}")
        msg = AIMessage(content=f"RAG search failed: {str(e)}")
        return {"messages": state["messages"] + [msg], "llm": state.get("llm")}


async def ingest_node(state):
    """Ingest content into RAG"""
    logger = logging.getLogger("mcp_client")

    msg = AIMessage(content="Ingest functionality placeholder")
    return {
        "messages": state["messages"] + [msg],
        "tools": state.get("tools", {}),
        "llm": state.get("llm"),
        "ingest_completed": True,
    }


def create_langgraph_agent(llm_with_tools, tools):
    """Create a LangGraph agent with tool routing"""

    logger = logging.getLogger("mcp_client")

    async def call_model(state):
        """Node that calls the LLM"""
        logger.info(f"🤖 Calling model with {len(state['messages'])} messages")

        start_time = time.time()
        try:
            response = await llm_with_tools.ainvoke(state["messages"])
            duration = time.time() - start_time

            # Track LLM metrics if available
            if METRICS_AVAILABLE:
                metrics["llm_calls"] += 1
                metrics["llm_times"].append(duration)

            logger.info(f"✅ Model response received in {duration:.2f}s")
            return {"messages": state["messages"] + [response]}
        except Exception as e:
            duration = time.time() - start_time
            if METRICS_AVAILABLE:
                metrics["llm_errors"] += 1
                metrics["llm_times"].append(duration)
            logger.error(f"❌ Model call failed after {duration:.2f}s: {e}")
            raise

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

        # Track tool calls from the new messages
        if METRICS_AVAILABLE:
            for msg in new_messages:
                if isinstance(msg, AIMessage) and hasattr(msg, 'tool_calls'):
                    for tool_call in msg.tool_calls:
                        tool_name = tool_call.get('name', 'unknown')
                        metrics["tool_calls"][tool_name] += 1
                        logger.info(f"🔧 Tool called: {tool_name}")

        # Reset loop count
        conversation_state["loop_count"] = 0

        # Track successful agent run
        if METRICS_AVAILABLE:
            duration = time.time() - start_time
            metrics["agent_times"].append(duration)
            logger.info(f"✅ Agent run completed in {duration:.2f}s")

        # Debug: Log final state
        logger.info(f"📨 Final conversation has {len(conversation_state['messages'])} messages")
        for i, msg in enumerate(conversation_state['messages'][-5:]):  # Only log last 5
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