    ┌──────────────────────────┐
    │      START (LLM)         │
    └─────────────┬────────────┘
                  │
                  ▼
       ┌──────────────────────┐
       │  INTENT FILTERING    │
       │ (reduce tool count)  │
       └───────┬──────────────┘
               │
               ▼
       ┌──────────────────────┐
       │  DOES LLM WANT A     │
       │     TOOL CALL?       │
       └───────┬──────────────┘
               │ yes
               ▼
       ┌──────────────────────┐
       │   FORMAT TOOL CALL   │
       │ (JSON schema match)  │
       └───────┬──────────────┘
               │
               ▼
       ┌──────────────────────┐
       │   ROUTER CHECK       │
       │ (tool calls first)   │
       └───────┬──────────────┘
               │
               ▼
       ┌──────────────────────┐
       │   TOOLNODE EXEC      │
       │ (LangGraph built-in) │
       └───────┬──────────────┘
               │
               ▼
       ┌──────────────────────┐
       │   MCP SERVER EXEC    │
       └───────┬──────────────┘
               │
               ▼
       ┌──────────────────────┐
       │  RETURN TOOL RESULT  │
       └───────┬──────────────┘
               │
               ▼
       ┌──────────────────────┐
       │   FEED BACK TO LLM   │
       └───────┬──────────────┘
               │
               ▼
       ┌──────────────────────┐
       │  DOES LLM NEED MORE  │
       │       TOOLS?         │
       └───────┬───────┬──────┘
               │yes    │no
               ▼       ▼
       (loop back)   ┌───────────────┐
                     │   FINALIZE    │
                     └───────────────┘

* Intent Filter → LLM → Router → ToolNode → MCP Server → Result → LLM → Repeat → Finalize