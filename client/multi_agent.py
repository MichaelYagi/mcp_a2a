"""
Multi-Agent Execution System
Orchestrates multiple specialized agents working together on complex tasks
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

from langchain_core.messages import HumanMessage, AIMessage, SystemMessage


class AgentRole(Enum):
    """Defines different agent specializations"""
    ORCHESTRATOR = "orchestrator"  # Coordinates other agents
    RESEARCHER = "researcher"      # Web search, RAG, information gathering
    CODER = "coder"               # Code generation, technical tasks
    ANALYST = "analyst"           # Data analysis, interpretation
    WRITER = "writer"             # Content creation, documentation
    PLANNER = "planner"           # Task decomposition, planning


@dataclass
class AgentTask:
    """Represents a task for an agent"""
    task_id: str
    role: AgentRole
    description: str
    context: Dict[str, Any]
    dependencies: List[str] = None  # Task IDs this depends on
    result: Optional[Any] = None
    status: str = "pending"  # pending, running, completed, failed
    start_time: Optional[float] = None
    end_time: Optional[float] = None

    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []


class MultiAgentOrchestrator:
    """
    Orchestrates multiple specialized agents to work on complex tasks
    """

    def __init__(self, base_llm, tools, logger: logging.Logger):
        self.base_llm = base_llm

        # Handle tools as either list or dict
        if isinstance(tools, dict):
            self.tools = list(tools.values())
        else:
            self.tools = tools

        self.logger = logger

        # Create specialized agents with different system prompts
        self.agents = self._create_specialized_agents()

        # Task management
        self.tasks: Dict[str, AgentTask] = {}
        self.task_results: Dict[str, Any] = {}

    def _create_specialized_agents(self) -> Dict[AgentRole, Any]:
        """Create specialized agents with role-specific prompts and tools"""

        agents = {}

        # System prompts for each role
        prompts = {
            AgentRole.ORCHESTRATOR: """You are an Orchestrator Agent. Your role is to:
1. Break down complex tasks into smaller, manageable subtasks
2. Assign subtasks to specialized agents (Researcher, Coder, Analyst, Writer, Planner)
3. Coordinate execution order based on dependencies
4. Aggregate results from all agents

When given a task, create a detailed execution plan with subtasks.
Respond in JSON format:
{
  "subtasks": [
    {
      "id": "task_1",
      "role": "researcher",
      "description": "...",
      "dependencies": []
    }
  ]
}

If this is a simple task that doesn't need multiple agents, respond with:
{"subtasks": []}""",

            AgentRole.RESEARCHER: """You are a Researcher Agent. Your role is to:
1. Search for information using RAG and web search tools
2. Gather relevant data from multiple sources
3. Summarize findings clearly and concisely
4. Cite sources when available

Focus on accuracy and thoroughness.""",

            AgentRole.CODER: """You are a Coder Agent. Your role is to:
1. Write clean, efficient code
2. Follow best practices and patterns
3. Add helpful comments and documentation
4. Test and validate solutions

Focus on code quality and maintainability.""",

            AgentRole.ANALYST: """You are an Analyst Agent. Your role is to:
1. Analyze data and identify patterns
2. Create visualizations and summaries
3. Draw insights and conclusions
4. Present findings clearly

Focus on clarity and actionable insights.""",

            AgentRole.WRITER: """You are a Writer Agent. Your role is to:
1. Create clear, engaging content
2. Structure information logically
3. Adapt tone to audience
4. Edit and refine output

Focus on clarity and readability.""",

            AgentRole.PLANNER: """You are a Planner Agent. Your role is to:
1. Decompose complex tasks into steps
2. Identify dependencies and order
3. Estimate time and resources
4. Create execution roadmaps

Focus on organization and feasibility.""",
        }

        for role, prompt in prompts.items():
            # Filter tools based on agent role
            agent_tools = self._get_tools_for_role(role)

            # Create agent with role-specific tools
            if agent_tools:
                agents[role] = self.base_llm.bind_tools(agent_tools)
            else:
                agents[role] = self.base_llm

            self.logger.info(f"✅ Created {role.value} agent with {len(agent_tools)} tools")

        return agents

    def _get_tools_for_role(self, role: AgentRole) -> List:
        """Get appropriate tools for each agent role"""

        # Tool mappings for each role
        role_tools = {
            AgentRole.ORCHESTRATOR: [],  # No tools, just planning

            AgentRole.RESEARCHER: [
                "rag_search_tool", "search_entries", "search_semantic",
                "semantic_media_search_text", "get_weather_tool"
            ],

            AgentRole.CODER: [
                "rag_search_tool",  # For code examples
            ],

            AgentRole.ANALYST: [
                "rag_search_tool", "search_entries",
            ],

            AgentRole.WRITER: [
                "rag_search_tool", "search_entries",
            ],

            AgentRole.PLANNER: [
                "list_todo_items", "add_todo_item",
            ],
        }

        tool_names = role_tools.get(role, [])

        # Filter available tools
        available_tools = []
        for tool in self.tools:
            if hasattr(tool, 'name') and tool.name in tool_names:
                available_tools.append(tool)

        return available_tools

    async def execute(self, user_request: str) -> str:
        """
        Main entry point for multi-agent execution
        """

        self.logger.info(f"🎭 Multi-agent execution started: {user_request}")
        start_time = time.time()

        try:
            # Step 1: Create execution plan
            plan = await self._create_execution_plan(user_request)

            if not plan:
                return await self._fallback_single_agent(user_request)

            # Step 2: Execute tasks
            results = await self._execute_tasks(plan)

            # Step 3: Aggregate results
            final_response = await self._aggregate_results(user_request, results)

            duration = time.time() - start_time
            self.logger.info(f"✅ Multi-agent execution completed in {duration:.2f}s")

            return final_response

        except Exception as e:
            self.logger.error(f"❌ Multi-agent execution failed: {e}")
            import traceback
            traceback.print_exc()
            return await self._fallback_single_agent(user_request)

    async def _create_execution_plan(self, user_request: str) -> Optional[List[AgentTask]]:
        """Use orchestrator to create execution plan"""

        self.logger.info("📋 Creating execution plan...")

        orchestrator = self.agents[AgentRole.ORCHESTRATOR]

        planning_prompt = f"""Given this user request: "{user_request}"

Create an execution plan by breaking it into subtasks.

Respond ONLY with JSON in this format:
{{
  "subtasks": [
    {{
      "id": "task_1",
      "role": "researcher",
      "description": "Detailed task description",
      "dependencies": []
    }}
  ]
}}

Available roles: researcher, coder, analyst, writer, planner

If this is a simple task that doesn't need multiple agents, respond with:
{{"subtasks": []}}"""

        try:
            response = await orchestrator.ainvoke([
                SystemMessage(content=self._get_system_prompt(AgentRole.ORCHESTRATOR)),
                HumanMessage(content=planning_prompt)
            ])

            # Parse JSON response
            import json
            import re

            content = response.content.strip()

            # Extract JSON if wrapped in markdown
            json_match = re.search(r'```json\s*(.*?)\s*```', content, re.DOTALL)
            if json_match:
                content = json_match.group(1)

            plan_data = json.loads(content)
            subtasks = plan_data.get("subtasks", [])

            if not subtasks:
                self.logger.info("📋 Simple task, using single agent")
                return None

            # Convert to AgentTask objects
            tasks = []
            for i, subtask in enumerate(subtasks):
                role_str = subtask.get("role", "researcher")
                try:
                    role = AgentRole(role_str)
                except ValueError:
                    role = AgentRole.RESEARCHER

                task = AgentTask(
                    task_id=subtask.get("id", f"task_{i}"),
                    role=role,
                    description=subtask.get("description", ""),
                    context={"user_request": user_request},
                    dependencies=subtask.get("dependencies", [])
                )
                tasks.append(task)
                self.tasks[task.task_id] = task

            self.logger.info(f"📋 Created plan with {len(tasks)} subtasks")
            for task in tasks:
                self.logger.info(f"  - {task.task_id}: {task.role.value} - {task.description[:50]}...")

            return tasks

        except Exception as e:
            self.logger.error(f"❌ Failed to create plan: {e}")
            import traceback
            traceback.print_exc()
            return None

    async def _execute_tasks(self, tasks: List[AgentTask]) -> Dict[str, Any]:
        """Execute tasks respecting dependencies"""

        self.logger.info(f"⚙️ Executing {len(tasks)} tasks...")

        completed = set()
        results = {}

        # Execute tasks in waves based on dependencies
        while len(completed) < len(tasks):
            # Find tasks that can run (dependencies met)
            ready_tasks = [
                task for task in tasks
                if task.task_id not in completed
                and all(dep in completed for dep in task.dependencies)
            ]

            if not ready_tasks:
                self.logger.error("❌ Dependency deadlock detected")
                break

            # Execute ready tasks in parallel
            self.logger.info(f"⚙️ Executing {len(ready_tasks)} parallel tasks...")

            task_coroutines = [
                self._execute_single_task(task, results)
                for task in ready_tasks
            ]

            task_results = await asyncio.gather(*task_coroutines, return_exceptions=True)

            # Mark completed
            for task, result in zip(ready_tasks, task_results):
                if isinstance(result, Exception):
                    self.logger.error(f"❌ Task {task.task_id} failed: {result}")
                    results[task.task_id] = f"Error: {str(result)}"
                else:
                    results[task.task_id] = result
                    self.logger.info(f"✅ Task {task.task_id} completed")

                completed.add(task.task_id)

        return results

    async def _execute_single_task(self, task: AgentTask, previous_results: Dict) -> str:
        """Execute a single agent task"""

        task.status = "running"
        task.start_time = time.time()

        self.logger.info(f"🤖 {task.role.value} executing: {task.description[:50]}...")

        try:
            agent = self.agents[task.role]

            # Build context from previous results
            context_info = ""
            for dep_id in task.dependencies:
                if dep_id in previous_results:
                    context_info += f"\n\nResult from {dep_id}:\n{previous_results[dep_id]}"

            # Create prompt with context
            prompt = f"""Task: {task.description}

User's original request: {task.context.get('user_request', '')}
{context_info}

Provide a clear, concise response for this specific subtask."""

            response = await agent.ainvoke([
                SystemMessage(content=self._get_system_prompt(task.role)),
                HumanMessage(content=prompt)
            ])

            task.result = response.content
            task.status = "completed"
            task.end_time = time.time()

            duration = task.end_time - task.start_time
            self.logger.info(f"✅ {task.role.value} completed in {duration:.2f}s")

            return response.content

        except Exception as e:
            task.status = "failed"
            task.end_time = time.time()
            self.logger.error(f"❌ Task {task.task_id} failed: {e}")
            raise

    async def _aggregate_results(self, user_request: str, results: Dict[str, Any]) -> str:
        """Aggregate results from all agents into final response"""

        self.logger.info("📊 Aggregating results...")

        orchestrator = self.agents[AgentRole.ORCHESTRATOR]

        # Build summary of all results
        results_summary = ""
        for task_id, result in results.items():
            task = self.tasks.get(task_id)
            if task:
                results_summary += f"\n\n### {task.role.value.title()} ({task_id}):\n{result}"

        aggregation_prompt = f"""User's original request: "{user_request}"

Results from specialized agents:
{results_summary}

Synthesize these results into a coherent, final response that directly answers the user's request.
Focus on clarity and completeness. Remove any redundancy."""

        response = await orchestrator.ainvoke([
            SystemMessage(content="You are synthesizing results from multiple agents. Create a clear, unified response."),
            HumanMessage(content=aggregation_prompt)
        ])

        return response.content

    async def _fallback_single_agent(self, user_request: str) -> str:
        """Fallback to single agent if multi-agent fails"""

        self.logger.info("🔄 Falling back to single agent")

        researcher = self.agents[AgentRole.RESEARCHER]
        response = await researcher.ainvoke([
            SystemMessage(content=self._get_system_prompt(AgentRole.RESEARCHER)),
            HumanMessage(content=user_request)
        ])

        return response.content

    def _get_system_prompt(self, role: AgentRole) -> str:
        """Get system prompt for a specific role"""

        prompts = {
            AgentRole.ORCHESTRATOR: "You are an Orchestrator Agent coordinating multiple specialized agents.",
            AgentRole.RESEARCHER: "You are a Researcher Agent focused on gathering accurate information.",
            AgentRole.CODER: "You are a Coder Agent focused on writing quality code.",
            AgentRole.ANALYST: "You are an Analyst Agent focused on data analysis and insights.",
            AgentRole.WRITER: "You are a Writer Agent focused on clear communication.",
            AgentRole.PLANNER: "You are a Planner Agent focused on organizing and planning tasks.",
        }

        return prompts.get(role, "You are a helpful AI assistant.")


async def should_use_multi_agent(user_request: str) -> bool:
    """
    Determine if a request should use multi-agent execution
    """

    request_lower = user_request.lower()

    # Indicators of complex multi-step tasks
    multi_step_indicators = [
        " and then ",
        " then ",
        " after that ",
        " next ",
        "first.*then",
        "research.*analyze",
        "find.*summarize",
        "gather.*create",
        "search.*write",
    ]

    import re
    for indicator in multi_step_indicators:
        if re.search(indicator, request_lower):
            return True

    # Complex task keywords
    complex_keywords = [
        "comprehensive", "detailed analysis", "full report",
        "research and", "analyze and", "compare and"
    ]

    if any(keyword in request_lower for keyword in complex_keywords):
        return True

    # Check word count (long requests often need breakdown)
    if len(user_request.split()) > 30:
        return True

    return False