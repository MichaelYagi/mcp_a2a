    ┌──────────────────────────────────────────────┐
    │            INTENT FILTERING                  │
    │      (langgraph.py filter_tools_by_intent)   │
    └───────────────────────┬──────────────────────┘
                            │
                            │ user_message
                            ▼
                 ┌──────────────────────┐
                 │  DETECT INTENT       │
                 │  (keyword matching)  │
                 └───────────┬──────────┘
                             │
           ┌─────────────────┼─────────────────┐
           │                 │                 │
           ▼                 ▼                 ▼
    ┌─────────────┐   ┌─────────────┐   ┌─────────────┐
    │  INGEST     │   │  MEDIA      │   │  DEFAULT    │
    │  Intent     │   │  Intent     │   │  (no filter)│
    └──────┬──────┘   └──────┬──────┘   └──────┬──────┘
           │                 │                 │
           │                 │                 │
           ▼                 ▼                 ▼

    INGEST INTENT:
    Keywords: "ingest", "subtitle", "plex", "batch", "process", "extract"
    Filtered Tools (6):
      ├─ rag_search_tool
      ├─ plex_ingest_batch
      ├─ plex_find_unprocessed
      ├─ plex_ingest_items
      ├─ plex_ingest_single
      └─ plex_get_stats

           │
           ▼
    Reduces: 40 tools → 6 tools (85% reduction)

    MEDIA INTENT:
    Keywords: "movie", "show", "film", "watch", "scene", "find"
    Filtered Tools (8):
      ├─ rag_search_tool
      ├─ semantic_media_search_text
      ├─ semantic_media_search_vector
      ├─ semantic_scene_location
      ├─ semantic_mood_recommendation
      ├─ plex_find_unprocessed
      ├─ plex_get_stats
      └─ search_entries

           │
           ▼
    Reduces: 40 tools → 8 tools (80% reduction)

    DEFAULT (NO FILTER):
    Keywords: none matched
    Filtered Tools: ALL (40+ tools)

           │
           ▼
    No reduction: 40 tools → 40 tools

BENEFITS:
* Reduces LLM confusion (fewer tools to choose from)
* Faster LLM inference (smaller tool list)
* Better tool selection accuracy
* Prevents wrong tool usage

DETECTION LOGIC:
1. Check for INGEST keywords first (highest priority)
2. If not INGEST, check for MEDIA keywords
3. If no match, return all tools

EXAMPLE QUERIES:
"Ingest 2 items" → INGEST → 6 tools
"Find action movies" → MEDIA → 8 tools
"What's the weather?" → DEFAULT → 40 tools