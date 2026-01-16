from typing import Any, Dict
from langchain_core.tools import Tool
from client.a2a_client import A2AClient


def make_a2a_tool(a2a_client: A2AClient, tool_def: Dict[str, Any]):
    """
    Create a LangChain-compatible tool that forwards calls to a remote A2A agent.
    This version:
      - Accepts exactly one positional argument (required by LangChain)
      - Avoids double-prefixing
      - Handles async execution correctly
      - Passes structured input through unchanged
    """

    # Use the remote tool name directly (no double prefixing)
    remote_name = tool_def["name"]
    local_name = f"a2a_{remote_name}"

    description = tool_def.get(
        "description",
        f"Remote A2A tool: {remote_name}"
    )

    async def _run(input):
        """
        LangChain always passes a single positional argument.
        For structured tools, this will be a dict.
        """
        if not isinstance(input, dict):
            raise ValueError(
                f"A2A tool '{local_name}' expected dict input, got: {input!r}"
            )

        # Forward the call to the remote A2A agent
        return await a2a_client.call(remote_name, input)

    # Wrap in a LangChain Tool
    return Tool(
        name=local_name,
        description=description,
        func=_run,
    )