"""
Shared Commands Module
Handles command processing for both CLI and WebSocket
"""

from langchain_core.messages import SystemMessage


def get_commands_list():
    """Get list of available commands"""
    return [
        ":commands - List all available commands",
        ":tools - List all available tools",
        ":tool <tool> - Get the tool description",
        ":model - View the current active model",
        ":model <model> - Use the model passed",
        ":models - List available models",
        ":clear history - Clear the chat history"
    ]


def get_tools_list(tools):
    """Get formatted list of all tools"""
    lines = [f"🛠 Found {len(tools)} MCP tools:"]
    for t in tools:
        lines.append(f"  - {t.name}")
    return "\n".join(lines)


def get_tool_description(tools, tool_name):
    """Get description for a specific tool"""
    for t in tools:
        if t.name == tool_name:
            return f"  - {t.description}"
    return f"❌ MCP tool {tool_name} not found"


async def handle_command(query, tools, model_name, conversation_state, models_module, system_prompt, agent_ref=None,
                         create_agent_fn=None, logger=None):
    """
    Process a command starting with ':'
    Returns: (handled: bool, response: str, new_agent: object or None, new_model: str or None)
    """
    query = query.strip()

    if query == ":commands":
        return True, "\n".join(get_commands_list()), None, None

    if query == ":tools":
        return True, get_tools_list(tools), None, None

    if query.startswith(":tool "):
        parts = query.split(maxsplit=1)
        if len(parts) == 1:
            return True, "Usage: :tool <tool_name>", None, None
        tool_name = parts[1]
        return True, get_tool_description(tools, tool_name), None, None

    if query == ":models":
        models = models_module.get_available_models()
        lines = ["Available models:"]
        for model in models:
            lines.append(f"  - {model}")
        return True, "\n".join(lines), None, None

    if query.startswith(":model "):
        parts = query.split(maxsplit=1)
        if len(parts) == 1:
            return True, "Usage: :model <model_name>", None, None

        new_model_name = parts[1]
        new_agent = await models_module.switch_model(new_model_name, tools, logger, create_agent_fn)
        if new_agent is None:
            return True, f"❌ Model '{new_model_name}' is not installed.", None, None

        return True, f"🤖 Model switched to {new_model_name}", new_agent, new_model_name

    if query == ":model":
        return True, f"Using model: {model_name}", None, None

    if query.startswith(":clear "):
        parts = query.split()
        if len(parts) == 1:
            return True, "Specify what to clear", None, None

        target = parts[1]
        if target == "history":
            conversation_state["messages"] = []
            conversation_state["messages"].append(SystemMessage(content=system_prompt))
            return True, "Chat history cleared.", None, None
        else:
            return True, f"Unknown clear target: {target}", None, None

    return False, None, None, None