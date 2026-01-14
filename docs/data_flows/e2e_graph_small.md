    USER
    │
    ▼
    WEB UI  ───────►  MCP CLIENT  ───────►  EXECUTION MODE
                                              │
                                    ┌─────────┴─────────┐
                                    │                   │
                                    ▼                   ▼
                            SINGLE-AGENT        MULTI-AGENT
                            (LangGraph)         (Orchestrator)
                                    │                   │
                                    │                   │ specialized agents
                                    │                   │ (parallel execution)
                                    │                   │
                                    └─────────┬─────────┘
                                              │
                                              │ calls tools
                                              ▼
                                           MCP SERVER

* Single-agent: LangGraph handles entire query
* Multi-agent: Orchestrator breaks down query → Specialized agents execute → Synthesis
* Both use MCP Server tools