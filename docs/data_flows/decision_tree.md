    ┌──────────────────────────────────────────────┐
    │              ROUTER DECISION                 │
    │         (langgraph.py router())              │
    └───────────────────────┬──────────────────────┘
                            │
                            │ last_message = AIMessage
                            ▼
                 ┌──────────────────────┐
                 │  CHECK TOOL CALLS    │
                 │  (HIGHEST PRIORITY)  │
                 └───────────┬──────────┘
                             │
                   ┌─────────┴─────────┐
                   │                   │
                   ▼ YES               ▼ NO
         ┌──────────────────┐   ┌──────────────────┐
         │  ROUTE: "tools"  │   │  CHECK CONTENT   │
         │  Execute tools   │   │  (has text?)     │
         └──────────────────┘   └────────┬─────────┘
                                         │
                               ┌─────────┴─────────┐
                               │                   │
                               ▼ NO                ▼ YES
                     ┌──────────────────┐   ┌──────────────────┐
                     │  ROUTE: END      │   │  CHECK QUERY     │
                     │  Finalize        │   │  (original msg)  │
                     └──────────────────┘   └────────┬─────────┘
                                                     │
                                           ┌─────────┴─────────┐
                                           │                   │
                                           ▼                   ▼
                               ┌────────────────────┐   ┌────────────────────┐
                               │  CHECK INGEST      │   │  CHECK MULTI-STEP  │
                               │  (keywords)        │   │  (patterns)        │
                               └─────────┬──────────┘   └─────────┬──────────┘
                                         │                        │
                               ┌─────────┴─────────┐    ┌────────┴────────┐
                               │                   │    │                 │
                               ▼ YES               │    ▼ YES             │
                     ┌──────────────────┐          │  ┌──────────────────┐│
                     │  CHECK "AND THEN"│          │  │  ROUTE:          ││
                     │  in query        │          │  │  "multi_agent"   ││
                     └─────────┬────────┘          │  └──────────────────┘│
                               │                   │                      │
                     ┌─────────┴─────────┐         │                      │
                     │                   │         │                      │
                     ▼ YES               ▼ NO      ▼ NO                   ▼ NO
           ┌──────────────────┐   ┌──────────────────┐      ┌──────────────────┐
           │  ROUTE:          │   │  ROUTE:          │      │  ROUTE: END      │
           │  "multi_agent"   │   │  "agent"         │      │  Finalize        │
           │  Complex query   │   │  Continue loop   │      └──────────────────┘
           └──────────────────┘   └──────────────────┘

PRIORITY ORDER:
1. Tool calls (if present) → "tools"
2. No content → "end"
3. INGEST intent + multi-step → "multi_agent"
4. Multi-step patterns → "multi_agent"
5. INGEST intent → "agent" (continue)
6. Default → "end"

KEYWORDS:
* INGEST: "ingest", "subtitle", "plex", "batch"
* MULTI-STEP: "and then", "then ", "after that", "next"

CRITICAL: Tool calls checked FIRST before all other logic