    ┌──────────────────────────────────────────────┐
    │              WEB UI (Browser)                │
    │        http://localhost:9000/index.html      │
    └───────────────────────┬──────────────────────┘
                            │
                            │ connects to 3 separate WebSocket servers
                            │
         ┌──────────────────┼──────────────────┐
         │                  │                  │
         ▼                  ▼                  ▼
    ┌─────────────┐   ┌─────────────┐   ┌─────────────┐
    │  WS: 8765   │   │  WS: 8766   │   │  WS: 8767   │
    │  CHAT       │   │  LOGS       │   │  METRICS    │
    └──────┬──────┘   └──────┬──────┘   └──────┬──────┘
           │                 │                 │
           │                 │                 │
           ▼                 ▼                 ▼

    CHAT WEBSOCKET (Port 8765):
    Handles: Bidirectional chat communication
    ├─ SENDS (Web UI → Server):
    │  ├─ user messages
    │  ├─ command requests (:tools, :stats, :multi)
    │  ├─ model switch requests
    │  ├─ history requests
    │  └─ system stats subscription
    │
    └─ RECEIVES (Server → Web UI):
       ├─ assistant messages
       ├─ command responses
       ├─ model switch confirmations
       ├─ history sync
       └─ system stats data

    Message Types:
      user                     → user message
      assistant_message        → AI response (with multi_agent flag)
      history_request         → request conversation history
      history_sync            → receive conversation history
      switch_model            → request model change
      model_switched          → confirm model change
      models_list             → available models
      subscribe_system_stats  → subscribe to monitoring
      system_stats            → CPU/GPU/RAM data

           │
           ▼
    Connection: Always active
    Reconnect: Auto on disconnect


    LOGS WEBSOCKET (Port 8766):
    Handles: Unidirectional log streaming (Server → Web UI)
    ├─ RECEIVES ONLY:
    │  ├─ log entries (timestamp, level, message)
    │  ├─ server events
    │  ├─ tool execution logs
    │  └─ multi-agent execution logs
    │
    └─ FILTERS:
       ├─ DEBUG (verbose)
       ├─ INFO (general)
       ├─ WARNING (issues)
       └─ ERROR (failures)
    
    Message Format:
    {
      "type": "log",
      "timestamp": "2024-01-14T10:30:45.123456",
      "level": "INFO",
      "name": "mcp_client",
      "message": "Multi-agent execution started"
    }

           │
           ▼
    Buffer: Last 500 entries in memory
    Auto-scroll: Configurable
    Reconnect: Every 3s on disconnect


    SYSTEM MONITOR (Via Chat WS):
    Handles: Real-time system metrics
    ├─ SUBSCRIPTION:
    │  └─ subscribe_system_stats message
    │
    └─ RECEIVES:
       ├─ CPU usage % and frequency
       ├─ GPU usage %, temp, VRAM
       ├─ RAM usage and total
       └─ Updates every 1 second
    
    Message Format:
    {
      "type": "system_stats",
      "cpu": {
        "usage_percent": 45,
        "frequency_ghz": 3.6
      },
      "gpu": {
        "usage_percent": 78,
        "temperature_c": 65,
        "memory_used_mb": 4096,
        "memory_total_mb": 12288
      },
      "memory": {
        "percent": 62,
        "used_gb": 9.8,
        "total_gb": 16.0
      }
    }

           │
           ▼
    Update Rate: 1 second
    Progressive bars with color coding


ARCHITECTURE BENEFITS:
* Separation of concerns (chat vs logs vs metrics)
* Independent reconnection strategies
* No cross-contamination of data streams
* Efficient buffering per stream
* Scales to multiple clients

CONNECTION STATE:
All streams: localhost only by default
Network access: Requires firewall rules
Multiple clients: Supported on all streams