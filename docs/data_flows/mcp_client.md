                         ┌──────────────────────────┐
                         │        MCP CLIENT        │
                         │ (Bridge + Tool Registry) │
                         └─────────────┬────────────┘
                                       │
                                       │ connects to
                                       ▼
                         ┌──────────────────────────┐
                         │       MCP SERVER         │
                         │   (Tool Provider)        │
                         └─────────────┬────────────┘
                                       │
                                       │ registers tools
                                       ▼
        ┌───────────────────────────────────────────────────────────┐
        │                    CLIENT TOOL REGISTRY                   │
        │           (local representation of MCP tools)             │
        └───────────────────────────────────────────────────────────┘
                                       │
                                       │ provides tools to
                                       ▼

        ┌───────────────────────────────────────────────────────────┐
        │                     EXECUTION MODE                        │
        │           (Single-Agent or Multi-Agent)                   │
        └───────────────────────────────────────────────────────────┘
            │                                         │
            │ Single                                  │ Multi
            ▼                                         ▼
    ┌────────────────┐                     ┌──────────────────────┐
    │  LANGGRAPH     │                     │  MULTI-AGENT         │
    │  AGENT         │                     │  ORCHESTRATOR        │
    │                │                     │                      │
    │  Intent Filter │                     │  Task Decomposition  │
    │  LLM Reasoning │                     │  Specialized Agents  │
    │  Router        │                     │  Parallel Execution  │
    │  ToolNode      │                     │  Result Synthesis    │
    │  Finalizer     │                     │                      │
    └────────┬───────┘                     └──────────┬───────────┘
             │                                        │
             │ both invoke tools via                  │
             └────────────────┬───────────────────────┘
                              │
                              ▼
        ┌───────────────────────────────────────────────────────────┐
        │                     MCP CLIENT API                        │
        │ (send tool calls, receive results, stream logs/metrics)   │
        └───────────────────────────────────────────────────────────┘
                                       │
                                       │ streams to
                                       ▼

                         ┌──────────────────────────┐
                         │         WEB UI           │
                         │ (Chat, Logs, Metrics)    │
                         └──────────────────────────┘

* MCP Client bridges Web UI and execution modes
* Single-agent: LangGraph state machine
* Multi-agent: Orchestrator + specialized agents
* Both modes use same MCP Server tools
* Results stream to Web UI