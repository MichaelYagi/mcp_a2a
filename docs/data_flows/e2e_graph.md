    ┌──────────────────────────────────────────────────────────────────────────┐
    │                                WEB UI                                    │
    │          (Chat, Logs, Metrics, Multi-Agent Toggle)                       │
    └───────────────────────────────┬──────────────────────────────────────────┘
                                    │  WebSocket / HTTP
                                    ▼
    ┌──────────────────────────────────────────────────────────────────────────┐
    │                               MCP CLIENT                                 │
    │              (Bridge between UI ↔ Agent ↔ MCP Server)                    │
    └───────────────┬──────────────────────────────────────────────────────────┘
                    │ registers tools with
                    ▼
    ┌──────────────────────────────────────────────────────────────────────────┐
    │                         CLIENT TOOL REGISTRY                             │
    │              (Local representation of MCP tools)                         │
    └───────────────┬──────────────────────────────────────────────────────────┘
                    │ provides tools to
                    ▼
    ┌──────────────────────────────────────────────────────────────────────────┐
    │                          EXECUTION MODE                                  │
    │           (Single-Agent or Multi-Agent based on query)                   │
    └───────────────┬──────────────────────────────────────────────────────────┘
                    │
        ┌───────────┴────────────┐
        │                        │
        ▼                        ▼
    ┌─────────────────┐   ┌──────────────────────────────────────┐
    │  SINGLE-AGENT   │   │        MULTI-AGENT                   │
    │  (LangGraph)    │   │     (Orchestrator + Agents)          │
    └────────┬────────┘   └─────────┬────────────────────────────┘
             │                      │
             │                      │ creates plan
             │                      ▼
             │            ┌──────────────────────────┐
             │            │  Task Decomposition      │
             │            │  (Orchestrator)          │
             │            └─────────┬────────────────┘
             │                      │
             │                      │ executes in parallel
             │                      ▼
             │            ┌──────────────────────────────────────┐
             │            │    Specialized Agents                │
             │            │  (Researcher, Coder, Analyst,        │
             │            │   Writer, Planner, Plex Ingester)    │
             │            └─────────┬────────────────────────────┘
             │                      │
             │                      │ aggregate results
             │                      ▼
             │            ┌──────────────────────────┐
             │            │  Final Synthesis         │
             │            │  (Orchestrator)          │
             │            └─────────┬────────────────┘
             │                      │
             └──────────────────────┘
                          │
                          ▼
    ┌──────────────────────────────────────────────────────────────────────────┐
    │                            AGENT NODES                                   │
    │         (Intent Filter → LLM → Router → ToolNode → LLM)                  │
    └───────────────┬──────────────────────────────────────────────────────────┘
                    │ invokes tools via
                    ▼
    ┌──────────────────────────────────────────────────────────────────────────┐
    │                               MCP SERVER                                 │
    │            (Tool Provider: RAG, Plex, Weather, System)                   │
    └───────────────┬──────────────────────────────────────────────────────────┘
                    │ exposes
                    ▼
    ┌──────────────────────────────────────────────────────────────────────────┐
    │                                   TOOLS                                  │
    └──────────────────────────────────────────────────────────────────────────┘
           │                     │                        │
           ▼                     ▼                        ▼

    ┌──────────────────┐   ┌──────────────────┐   ┌──────────────────┐
    │ RAG Search       │   │ Plex Ingestion   │   │ Weather API      │
    │ (bge-large)      │   │ (Subtitle/Meta)  │   │                  │
    └──────────────────┘   └──────────────────┘   └──────────────────┘
           │                     │
           │ queries             │ fetches
           ▼                     ▼

    ┌──────────────────┐   ┌──────────────────┐
    │ Vector Database  │   │ Plex Library     │
    │ (LanceDB)        │   │ (Media Server)   │
    └──────────────────┘   └──────────────────┘


    ┌──────────────────────────────────────────────────────────────────────────┐
    │                         WEBSOCKET STREAMS                                │
    │              (Logs, Metrics, System Monitor)                             │
    └──────────────────────────────────────────────────────────────────────────┘

* Web UI controls execution mode via toggle
* Single-agent: Direct LangGraph execution
* Multi-agent: Orchestrator → Specialized agents → Parallel execution → Synthesis
* Both modes use same MCP Server tools
* Results stream back to Web UI