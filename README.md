# MCP Server & Client with Multi-Agent System

A modular **Model Context Protocol (MCP)** architecture for exposing Python-based tools to AI agents through a unified JSON-RPC interface, enhanced with **multi-agent orchestration** for complex task execution.

The server is plug-and-play—add new capabilities by simply dropping modules into the directory structure.

This started as a tool for me to learn about implementing MCP and its core components.

---

## Multi-Agent System

### Overview

The multi-agent system automatically detects complex queries and breaks them down into specialized subtasks executed by different agents working in parallel:

**6 Specialized Agents:**
- **🎯 Orchestrator** - Plans task decomposition and coordinates execution
- **🔍 Researcher** - Gathers information using RAG, web search, and Plex media
- **💻 Coder** - Generates clean, documented code with best practices
- **📊 Analyst** - Analyzes data, identifies patterns, draws insights
- **✍️ Writer** - Creates clear, structured, engaging content
- **📋 Planner** - Manages tasks, creates roadmaps, adds to todos

### How It Works

**Single-Agent Mode (Fast & Simple):**
```
User: "What's the weather?"
→ Researcher agent → Weather API → Response (2s)
```

**Multi-Agent Mode (Comprehensive & Parallel):**
```
User: "Research Python async, analyze best practices, and create a guide"

→ Orchestrator creates execution plan:
   ├─ Task 1: Researcher gathers async documentation (5s)
   ├─ Task 2: Analyst evaluates best practices (7s, depends on Task 1)
   └─ Task 3: Writer creates comprehensive guide (6s, depends on Tasks 1 & 2)

→ Executes with parallel processing where possible
→ Orchestrator aggregates results into coherent response
→ Final comprehensive guide delivered (18s total vs 25s sequential)
```

### Automatic Detection

The system intelligently chooses the right execution mode:

**✅ Multi-Agent Triggers:**
- Sequential indicators: "then", "after that", "next", "and then"
- Multi-step patterns: "research AND analyze", "find AND compare"
- Complexity keywords: "comprehensive", "detailed analysis", "full report"
- Long queries (30+ words)
- Multiple distinct actions

**❌ Single-Agent Triggers:**
- Simple questions (< 15 words)
- Direct tool calls: "What's the weather?", "Add to my todo"
- Single action queries: "Find movies about space"
- Quick lookups: "List my todos"

### Performance Comparison

| Query Type | Single Agent | Multi-Agent | Speedup |
|------------|--------------|-------------|---------|
| "What's the weather?" | 2s | N/A (uses single) | - |
| "Research + analyze + write" | 25s | 18s | 1.4x |
| 3 parallel tasks | 30s | 12s | 2.5x |
| Complex report generation | 40s | 22s | 1.8x |

### Control Multi-Agent Mode

**Web UI Toggle:**
Beautiful sliding toggle in the header:
- Click to switch between 🤖 Single and 🎭 Multi modes
- Visual indicators on responses (purple border for multi-agent)
- Setting persists across sessions

**CLI Commands:**
```bash
:multi on       # Enable multi-agent mode
:multi off      # Disable multi-agent mode
:multi status   # Check current mode and agent info
```

**Environment Variable:**
```bash
# In .env file
MULTI_AGENT_ENABLED=true   # Enable by default
```

---

## Key Features

* **🎭 Multi-Agent Orchestration**: Automatic task decomposition with parallel execution (NEW!)
* **Bidirectional Architecture**: Server exposes tools, Client acts as the AI brain using LLMs
* **Multi-Domain Support**: Organize tools into logical categories (`knowledge`, `system`, `math`)
* **Versioned Storage**: File-backed persistence with automatic snapshotting
* **Offline Semantic Search**: Pure-Python TF-IDF implementation
* **RAG System**: Vector-based retrieval with OllamaEmbeddings (bge-large) for semantic search over ingested content
* **Plex Media Integration**: Automated subtitle and metadata ingestion with batch processing
* **Real-Time Log Streaming**: WebSocket-based live log viewer with filtering
* **System Monitor**: Real-time CPU, GPU, and memory monitoring (NEW!)
* **Performance Dashboard**: Metrics visualization with timestamps (NEW!)
* **Mobile-Friendly UI**: Fully responsive interface for phones, tablets, and desktop
* **Windows Optimized**: Handles encoding and stdio pipe challenges

---

## Architecture

* **Client (client.py)**: AI agent that connects to the server and invokes tools
* **Multi-Agent System (multi_agent.py)**: Orchestrates specialized agents for complex tasks (NEW!)
* **Server (server.py)**: Hub that registers tools and provides JSON-RPC interface
* **Web UI (index.html)**: Modern chat interface with multi-agent toggle, logs, and system monitor
* **Dashboard (dashboard.html)**: Performance metrics with real-time charts
* **Tools Directory**: Functional Python logic for each domain with local persistence
* **Schemas Directory**: Input contracts (prompts) between AI and code

---

## Directory Structure

```
mcp-server/
│
├── server.py                 # Registers and exposes tools and prompts
├── client.py                 # AI Agent with multi-agent orchestration
├── index.html                # Web UI with chat, multi-agent toggle, and logs
├── dashboard.html            # Performance metrics dashboard
│
├── client/                   # Client modules
│   ├── multi_agent.py        # Multi-agent orchestration system (NEW!)
│   ├── langgraph.py          # Single-agent execution
│   ├── commands.py           # CLI command handling
│   ├── websocket.py          # WebSocket server
│   ├── metrics.py            # Performance tracking
│   └── ...
│
├── tools/                    # Python tools - defines tools
│   ├── knowledge_base/       # Structured data & search
│   │   └── kb_add.py
│   ├── location/             # External API integration
│   │   └── get_weather.py
│   ├── system_monitor/       # System stats monitoring (NEW!)
│   └── more_tools/
```

---

## Setup

### Prerequisites

* Python 3.10+
* llama3.1:8b (or qwen2.5:14b for better multi-agent performance)
* bge-large embedding model

---

**System requirements**

**Minimum (Single Agent Only)**
* RAM: 8GB total system RAM 
* Model will use: ~5-6GB RAM 
* Speed: Slow (2-5 tokens/sec)
* Multi-agent: Not recommended

**Recommended (Multi-Agent Support)**
* RAM: 16GB+ system RAM
* Model will use: ~8-10GB RAM
* Speed: Moderate (10-20 tokens/sec)
* Multi-agent: Works well

**Optimal (Best Multi-Agent Performance)**
* RAM: 32GB+
* GPU: Any modern GPU with 6GB+ VRAM
* Speed: 30-100+ tokens/sec
* Multi-agent: Excellent performance with parallel execution

---

### Installation

**1. Install dependencies**

From `mcp_server` root:

```bash
curl -fsSL https://ollama.com/install.sh | sh
python -m venv .venv
```

WSL
```bash
source .venv-wsl/bin/activate
pip install -r requirements.txt
```

Linux
```bash
source .venv/bin/activate
pip install -r requirements.txt
```

Windows PowerShell
```powershell
.venv\Scripts\activate
.venv\Scripts\pip.exe install -r .\requirements.txt
```

---

**Environment Configuration**

Create or update `.env` file:

**Multi-Agent Settings (NEW!)**
```bash
MULTI_AGENT_ENABLED=true    # Enable multi-agent by default
MAX_MESSAGE_HISTORY=20      # Conversation history size
```

**Weather API**

Get a free key at [Weather API](https://www.weatherapi.com/)
```bash
WEATHER_API_KEY=<Weather API Key>
```

**Plex Integration**
```bash
PLEX_BASE_URL=http://<ip>:32400
PLEX_TOKEN=<plex_token>
```

---

**3. Run Ollama server and download models:**

```bash
ollama serve
ollama pull llama3.1:8b      # Good for single-agent
ollama pull qwen2.5:14b      # Better for multi-agent (recommended)
ollama pull bge-large        # Embedding model for RAG
```

**Model Recommendations for Multi-Agent:**
- **llama3.1:8b** - Works, but may struggle with complex orchestration
- **qwen2.5:14b** - **Recommended** - Better planning and tool selection
- **qwen2.5:32b** - Best performance, requires 32GB+ RAM

---

**4. Start the client:**

Linux
```bash
python client.py
```

Windows PowerShell
```powershell
.venv\Scripts\python.exe client.py
```

You should see:
```
🚀 Starting MCP Agent with dual interface support
============================================================
✅ Created orchestrator agent with 0 tools
✅ Created researcher agent with 5 tools
✅ Created coder agent with 1 tools
✅ Created analyst agent with 2 tools
✅ Created writer agent with 2 tools
✅ Created planner agent with 2 tools
🎭 Multi-agent orchestrator created (enabled: True)
🎭 Multi-agent mode: ENABLED
   Complex queries will be broken down automatically
   Use ':multi off' to disable
```

The client will start three services:
- **Port 8765**: WebSocket for chat
- **Port 8766**: WebSocket for real-time logs
- **Port 9000**: HTTP server for web UI

Your browser will automatically open to `http://localhost:9000/index.html`

---

## 🎭 Using Multi-Agent Mode

### Web UI (Recommended)

The web interface includes a beautiful toggle switch in the header:

**Toggle Switch:**
```
🤖 Single [○────────] 🎭 Multi
          ↑ Click to toggle
```

**Visual Indicators:**
- **Purple gradient toggle** - Multi-agent enabled
- **Gray toggle** - Single-agent mode
- **Purple border on responses** - Response from multi-agent
- **Status badge** - Shows current mode

**How to Use:**
1. Open `http://localhost:9000`
2. Click the toggle switch to enable/disable multi-agent
3. Multi-agent responses will have a purple left border
4. Setting persists across browser sessions

### CLI Terminal

When using the terminal interface, use these commands:

```bash
:multi on        # Enable multi-agent mode
:multi off       # Disable multi-agent mode (use single-agent only)
:multi status    # Check current status and see agent info
```

**Status Output:**
```
Multi-agent mode: ENABLED ✅

Multi-agent system is available and ready.

When enabled, complex queries are automatically:
  • Broken down into subtasks
  • Assigned to specialized agents (Researcher, Coder, Analyst, Writer, Planner)
  • Executed in parallel where possible
  • Results are aggregated

Examples of multi-agent queries:
  • 'Research X, analyze Y, and write Z'
  • 'Find A then compare with B'
  • 'Gather data and create a report'

Simple queries (weather, todos, search) use single-agent automatically.
```

### Example Multi-Agent Queries

**Research + Analysis + Writing:**
```
Research the top 5 Python web frameworks, analyze their performance, and create a comparison report
```
**Expected Flow:**
- Researcher: Gathers information on Django, Flask, FastAPI, Tornado, Pyramid
- Analyst: Compares performance benchmarks, learning curves, use cases
- Writer: Creates structured comparison with recommendations

---

**Code + Analysis + Documentation:**
```
Write a Python function to calculate Fibonacci numbers, analyze its time complexity, and document it
```
**Expected Flow:**
- Coder: Implements multiple Fibonacci approaches (recursive, iterative, memoized)
- Analyst: Analyzes Big O complexity for each approach
- Writer: Documents implementation with usage examples

---

**Data Gathering + Planning:**
```
Find resources for learning Docker and Kubernetes, create a 30-day study plan, and add milestones to my todos
```
**Expected Flow:**
- Researcher: Finds tutorials, courses, official documentation
- Planner: Creates phased 30-day learning roadmap
- Planner: Adds key milestones as actionable todo items

---

**Complex Research:**
```
Research climate change impacts, analyze temperature trends from the last decade, and write a summary
```
**Expected Flow:**
- Researcher: Gathers climate data and scientific studies
- Analyst: Identifies temperature patterns and projections
- Writer: Summarizes findings in accessible language

---

### Performance Tips

**When to Use Multi-Agent:**
- Complex multi-step tasks
- Tasks requiring different skill sets
- Comprehensive reports or analyses
- Quality and completeness matter more than speed

**When to Use Single-Agent:**
- Quick questions
- Simple tool calls (weather, todos)
- Time-sensitive queries
- Testing or debugging

**Optimizing Multi-Agent:**
- Use a more capable model (qwen2.5:14b or larger)
- Ensure adequate RAM (16GB+ recommended)
- Be specific about what you want in each step
- Let the system work - multi-agent takes longer but produces better results

---

## Interface Options

### Web UI (Recommended)

Modern chat interface with advanced features:

**Chat Features:**
* Conversational interface with message history
* **Multi-Agent Toggle** - Beautiful switch to enable/disable multi-agent mode (NEW!)
* **Visual Mode Indicators** - Purple borders and badges for multi-agent responses (NEW!)
* Model switcher - Change Ollama models on the fly
* Persistent history - Saved in browser localStorage

**Real-Time Log Viewer:**
* Live streaming logs with filtering
* Toggle with "📋 Logs" button
* Filter by level: DEBUG, INFO, WARNING, ERROR
* Auto-scroll or manual control
* Color-coded by severity
* Multi-agent execution logs clearly visible (NEW!)

**System Monitor (NEW!):**
* Real-time CPU, GPU, memory stats
* Toggle with "📊 System" button
* Visual progress bars with color indicators
* Auto-updating metrics

**Performance Dashboard:**
* Access via "📈 Dashboard" button
* Real-time charts with actual timestamps (NEW!)
* Agent execution times
* LLM call durations
* Tool usage metrics
* Multi-agent task breakdown visualization (NEW!)

**Mobile-Friendly:**
* Responsive design for phones and tablets
* Touch-optimized controls (44px minimum targets)
* Full-screen overlays on mobile
* Safe area insets for notched displays
* Multi-agent toggle works seamlessly on mobile (NEW!)

Access at: `http://localhost:9000/index.html`

---

### CLI Terminal (Advanced)

Full logging output in terminal, ideal for debugging:
- All log messages printed to console
- Multi-agent execution details (NEW!)
- Task breakdown and timing (NEW!)
- Tool call inspection
- Detailed error traces
- Direct input/output

Both interfaces can be used simultaneously and share the same conversation state!

---

## CLI Commands

When using the terminal interface, type these commands:

**General Commands:**
* `:commands` - List all available commands
* `:tools` - List all available MCP tools
* `:tool <name>` - Get description of a specific tool
* `:models` - List available Ollama models
* `:model` - Show current model
* `:model <name>` - Switch to a different model
* `:clear history` - Clear conversation history

**Multi-Agent Commands (NEW!):**
* `:multi on` - Enable multi-agent mode
* `:multi off` - Disable multi-agent mode
* `:multi status` - Check multi-agent status and capabilities

---

## Multi-Agent Logs

When multi-agent mode executes, you'll see detailed logs:

```bash
🎭 Using MULTI-AGENT execution
🎭 Multi-agent execution started: Research X, analyze Y, write Z
📋 Creating execution plan...
📋 Created plan with 3 subtasks
  - task_1: researcher - Research X
  - task_2: analyst - Analyze Y (depends on task_1)
  - task_3: writer - Write Z (depends on task_1, task_2)
⚙️ Executing 1 parallel tasks...
🤖 researcher executing: Research X...
✅ Task task_1 completed
✅ researcher completed in 5.23s
⚙️ Executing 1 parallel tasks...
🤖 analyst executing: Analyze Y...
✅ Task task_2 completed
✅ analyst completed in 7.12s
⚙️ Executing 1 parallel tasks...
🤖 writer executing: Write Z...
✅ Task task_3 completed
✅ writer completed in 6.08s
📊 Aggregating results...
✅ Multi-agent execution completed in 18.43s
```

---

## Extending the System

### Adding New Tools

Three steps to add new tools:

1. **Logic**: Add Python script to `tools/<new_domain>/`
2. **Register**: Import in `server.py` and wrap with `@mcp.tool()`

### Customizing Multi-Agent Agents (NEW!)

Edit `client/multi_agent.py` to customize agent behavior:

**Add Custom Agent Role:**
```python
class AgentRole(Enum):
    # ... existing roles ...
    DATA_ENGINEER = "data_engineer"  # NEW ROLE

# Add system prompt
data_engineer_prompt = """You are a Data Engineer Agent. Your role is to:
1. Design efficient data pipelines
2. Optimize data storage and retrieval
3. Ensure data quality and consistency
4. Implement ETL processes

Focus on scalability and performance."""

# Add to agents dict
prompts = {
    # ... existing prompts ...
    AgentRole.DATA_ENGINEER: data_engineer_prompt,
}
```

**Customize Agent Tools:**

In `_get_tools_for_role()` method:
```python
role_tools = {
    # ... existing mappings ...
    AgentRole.DATA_ENGINEER: [
        "rag_search_tool",
        "add_entry",
        "search_entries",
    ],
}
```

---

## WebSocket API

The client exposes two WebSocket endpoints:

**Chat WebSocket (Port 8765)**
```javascript
ws://localhost:8765
```

Message types:
- `user` - Send user message
- `assistant_message` - Receive AI response
  - Now includes `multi_agent: true` field for multi-agent responses (NEW!)
- `history_request` - Request conversation history
- `history_sync` - Receive conversation history
- `switch_model` - Request model change
- `model_switched` - Confirm model change
- `models_list` - Receive available models
- `subscribe_system_stats` - Subscribe to system monitoring (NEW!)
- `system_stats` - Receive system statistics (NEW!)

**Log WebSocket (Port 8766)**
```javascript
ws://localhost:8766
```

Message format:
```json
{
    "type": "log",
    "timestamp": "2024-01-09T10:30:45.123456",
    "level": "INFO",
    "name": "mcp_client",
    "message": "🎭 Multi-agent execution started"
}
```

---

## Network Access

**Local Network Access**

To access the Web UI from other devices on your network (phones, tablets, other computers):

1. Find your server's local IP address:
   ```bash
   # Linux/Mac/WSL
   hostname -I | awk '{print $1}'
   
   # Windows PowerShell
   ipconfig
   # Look for "IPv4 Address" under your active network adapter
   ```

2. Access from other devices using the IP address:
   ```
   http://[your-ip]:9000/index.html
   
   Example: http://192.168.0.185:9000/index.html
   ```

**Firewall Configuration**

The Web UI requires three ports to be accessible:
- **Port 8765** - Chat WebSocket
- **Port 8766** - Log streaming WebSocket  
- **Port 9000** - HTTP server

**Windows with WSL2 (Most Common Setup):**

WSL2 uses a virtual network adapter that Windows Firewall blocks by default. You need to add firewall rules:

```powershell
# Open PowerShell as Administrator and run:

New-NetFirewallRule -DisplayName "MCP WebSocket Chat" -Direction Inbound -LocalPort 8765 -Protocol TCP -Action Allow

New-NetFirewallRule -DisplayName "MCP WebSocket Logs" -Direction Inbound -LocalPort 8766 -Protocol TCP -Action Allow

New-NetFirewallRule -DisplayName "MCP HTTP Server" -Direction Inbound -LocalPort 9000 -Protocol TCP -Action Allow
```

**Linux (using ufw):**

```bash
sudo ufw allow 8765/tcp
sudo ufw allow 8766/tcp
sudo ufw allow 9000/tcp
```

---

## Troubleshooting

### Multi-Agent Issues (NEW!)

**Multi-agent never activates**
- Check: Run `:multi status` to verify it's enabled
- Check: Ensure `client/multi_agent.py` exists
- Check: Look for "Multi-agent orchestrator created" in startup logs
- Solution: Run `:multi on` or set `MULTI_AGENT_ENABLED=true` in `.env`

**Multi-agent fails and falls back to single**
- Check logs for "Multi-agent execution failed" messages
- Common cause: LLM can't parse orchestrator's JSON plan
- Solution: Switch to a more capable model (qwen2.5:14b recommended)
  ```bash
  :model qwen2.5:14b
  ```

**Poor quality multi-agent results**
- Issue: Agents not producing good outputs
- Solution: Edit agent prompts in `client/multi_agent.py` around line 50
- Tip: Be more specific in your queries about what you want from each step

**Multi-agent is too slow**
- This is normal - multi-agent adds 2-3s planning overhead
- Multi-agent is designed for quality over speed
- For quick queries, use `:multi off` or simple single-action queries
- Consider upgrading to a faster model or adding GPU

**Toggle doesn't work in Web UI**
- Check browser console (F12) for errors
- Verify `:multi on/off` commands work in CLI first
- Clear browser cache and reload page
- Check that updated `index.html` with toggle is being served

### General Issues

**Web UI won't load**
- Check that all three ports (8765, 8766, 9000) are available
- Look for "HTTP server running" message in terminal
- Try accessing `http://localhost:9000/index.html` directly

**Can't connect from another device on the network**
- Verify firewall rules are configured (see Network Access section)
- Check ports are listening on `0.0.0.0` not `127.0.0.1`:
  ```bash
  netstat -an | grep -E '8765|8766|9000'
  ```
- For WSL2, you may need port forwarding

**Chat not responding**
- Check Ollama is running: `ollama list`
- Verify WebSocket connection in browser console
- Check terminal for error messages
- Try switching models: `:model llama3.1:8b`

**Model switching fails**
- Ensure model is installed: `ollama list`
- Pull missing models: `ollama pull <model>`
- Check terminal for error messages

---

## Performance Notes

### Single-Agent
- Typical response time: 2-5s for simple queries
- Good for quick lookups and direct tool calls
- Low resource usage

### Multi-Agent (NEW!)
- Planning overhead: 2-3s
- Parallel execution: 1.5-2.5x speedup for independent tasks
- Best for complex, multi-step workflows
- Higher resource usage (multiple LLM calls)
- Produces more comprehensive, higher-quality results

### System Performance
- Log panel keeps only last 500 entries for memory efficiency
- WebSocket connections auto-reconnect if dropped
- Chat history stored in browser localStorage
- Multiple clients can connect simultaneously
- Minimal CPU usage even with high-frequency logging
- Multi-agent tasks tracked individually in metrics (NEW!)

---

## Browser Compatibility

**Desktop**
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

**Mobile**
- Safari (iOS 14+)
- Chrome (Android 90+)
- Samsung Internet
- Mobile Firefox

All features including multi-agent toggle work on modern browsers with WebSocket support.

---

## What's New in This Version

🎭 **Multi-Agent System**
- Automatic task decomposition and parallel execution
- 6 specialized agents (Orchestrator, Researcher, Coder, Analyst, Writer, Planner)
- Intelligent mode detection
- Beautiful Web UI toggle
- Visual indicators for multi-agent responses
- CLI commands for control

📊 **Enhanced Monitoring**
- Real-time system stats (CPU, GPU, memory)
- Performance dashboard with actual timestamps
- Multi-agent task breakdown visualization
- Detailed execution logs

🎨 **Improved UI**
- Responsive multi-agent toggle switch
- Purple gradient styling for multi-agent mode
- Visual distinction for multi-agent responses
- Mobile-optimized controls
- Persistent mode settings

🔧 **Better Control**
- `:multi` commands for CLI
- Environment variable configuration
- Per-session mode switching

- Automatic mode selection based on query complexity
