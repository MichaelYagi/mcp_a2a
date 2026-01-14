                          ┌──────────────────────────┐
                          │        MCP SERVER        │
                          │  (Tool Provider Layer)   │
                          └─────────────┬────────────┘
                                        │
                                        │ exposes tools
                                        ▼
        ┌───────────────────────────────────────────────────────────┐
        │                           TOOLS                           │
        └───────────────────────────────────────────────────────────┘
            │                     │                     │
            │                     │                     │
            ▼                     ▼                     ▼

    ┌────────────────┐     ┌──────────────────┐     ┌──────────────────┐
    │  RAG Search    │     │   Plex Ingest    │     │   Weather API    │
    │   Tool         │     │     Tool         │     │      Tool        │
    └────────────────┘     └──────────────────┘     └──────────────────┘
             │                     │                     │
             │                     │                     │
             ▼                     ▼                     ▼

    ┌────────────────┐     ┌──────────────────┐     ┌──────────────────┐
    │  bge-large     │     │ Plex Library     │     │  External API    │
    │  Embedding     │     │ Subtitle Extract │     │                  │
    └────────────────┘     └──────────────────┘     └──────────────────┘
             │                     │
             ▼                     ▼
    ┌────────────────┐     ┌──────────────────┐
    │  LanceDB       │     │  Media Metadata  │
    │  Vector Search │     │                  │
    └────────────────┘     └──────────────────┘


            ┌──────────────────────────────────────────────────────────┐
            │                        LOGGING                           │
            │         (WebSocket stream of server events)              │
            └──────────────────────────────────────────────────────────┘


            ┌──────────────────────────────────────────────────────────┐
            │                        METRICS                           │
            │       (CPU/GPU/RAM monitoring via WebSocket)             │
            └──────────────────────────────────────────────────────────┘

* MCP Server exposes tools to client
* Tools execute specialized functions
* Results return to agent via MCP Client
* Logs and metrics stream to Web UI