    ┌──────────────────────────────────────────────┐
    │          MULTI-AGENT EXECUTION               │
    └───────────────────────┬──────────────────────┘
                            │
                            ▼
                 ┌──────────────────────┐
                 │  QUERY ANALYSIS      │
                 │ (should_use_multi)   │
                 └───────────┬──────────┘
                             │
                             │ triggers: "and then", "research AND analyze"
                             │ complex keywords, 30+ words
                             ▼
                 ┌──────────────────────┐
                 │  ORCHESTRATOR        │
                 │  (create plan)       │
                 └───────────┬──────────┘
                             │
                             │ LLM generates JSON plan
                             ▼
                 ┌──────────────────────┐
                 │  TASK BREAKDOWN      │
                 │  (subtasks array)    │
                 └───────────┬──────────┘
                             │
                             │ example: 3 tasks
                             ▼
        ┌────────────────────┼────────────────────┐
        │                    │                    │
        ▼                    ▼                    ▼
    ┌─────────────┐   ┌─────────────┐   ┌─────────────┐
    │  TASK 1     │   │  TASK 2     │   │  TASK 3     │
    │ Researcher  │   │ Analyst     │   │ Writer      │
    │ (no deps)   │   │ (deps: T1)  │   │ (deps: T1,2)│
    └──────┬──────┘   └──────┬──────┘   └──────┬──────┘
           │                 │                  │
           │ execute         │ wait for T1      │ wait for T1,T2
           ▼                 │                  │
    ┌─────────────┐          │                  │
    │ Researcher  │          │                  │
    │ Agent       │          │                  │
    │ (with tools)│          │                  │
    └──────┬──────┘          │                  │
           │                 │                  │
           │ result          │                  │
           ▼                 │                  │
    ┌─────────────┐          │                  │
    │ Task 1      │          │                  │
    │ Complete    │          │                  │
    └──────┬──────┘          │                  │
           │                 │                  │
           └─────────────────┤                  │
                             │                  │
                             │ now execute      │
                             ▼                  │
                      ┌─────────────┐           │
                      │ Analyst     │           │
                      │ Agent       │           │
                      │ (with tools)│           │
                      └──────┬──────┘           │
                             │                  │
                             │ result           │
                             ▼                  │
                      ┌─────────────┐           │
                      │ Task 2      │           │
                      │ Complete    │           │
                      └──────┬──────┘           │
                             │                  │
                             └──────────────────┤
                                                │
                                                │ now execute
                                                ▼
                                         ┌─────────────┐
                                         │ Writer      │
                                         │ Agent       │
                                         │ (with tools)│
                                         └──────┬──────┘
                                                │
                                                │ result
                                                ▼
                                         ┌─────────────┐
                                         │ Task 3      │
                                         │ Complete    │
                                         └──────┬──────┘
                                                │
                                                ▼
                 ┌──────────────────────────────────────┐
                 │  RESULT AGGREGATION                  │
                 │  (orchestrator synthesizes)          │
                 └───────────────────┬──────────────────┘
                                     │
                                     ▼
                 ┌──────────────────────────┐
                 │  FINAL RESPONSE          │
                 │  (coherent answer)       │
                 └──────────────────────────┘

* Query → Analysis → Plan → Parallel Execution (respecting deps) → Synthesis
* Each agent has access to MCP tools
* Dependency management ensures proper ordering
* Parallel execution where possible (Tasks with no dependencies run simultaneously)