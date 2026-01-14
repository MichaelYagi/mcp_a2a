    ┌──────────────────────────────────────────────┐
    │               LANGGRAPH AGENT                │
    │        (State Machine + Tool Router)         │
    └───────────────────────┬──────────────────────┘
                            │
                            ▼
                 ┌──────────────────────┐
                 │   INTENT FILTERING   │
                 │ (reduce tool count)  │
                 └───────────┬──────────┘
                             │
                             ▼
                 ┌──────────────────────┐
                 │   LLM REASONING      │
                 │ (decide tool calls)  │
                 └───────────┬──────────┘
                             │
                             │ has tool calls?
                             ▼
             ┌──────────────────────────────┬─────────────────────────────┐
             │                              │                             │
             ▼                              ▼                             ▼
    ┌──────────────────┐        ┌────────────────────┐        ┌────────────────────┐
    │  ROUTER NODE     │        │  TOOLNODE          │        │  FINALIZER NODE    │
    │ (tool calls      │        │ (invoke MCP tools) │        │ (produce answer)   │
    │  priority first) │        │                    │        │                    │
    └─────────┬────────┘        └──────────┬─────────┘        └───────────┬────────┘
              │                            │                              │
              │ routes to tools            │                              │
              └────────────────────────────┤                              │
                                           │                              │
                                           ▼                              │
                                ┌──────────────────────────┐              │
                                │   MCP CLIENT API         │              │
                                │ (execute tool via server)│              │
                                └───────────┬──────────────┘              │
                                            │                             │
                                            │ result back to LLM          │
                                            └─────────────────────────────┘

* Intent Filter → LLM → Router (tool calls first) → ToolNode → MCP Server → Result → LLM → Loop or Finalize