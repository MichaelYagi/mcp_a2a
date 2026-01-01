# Schema‑Aware Tool Usage Guide (For LLMs)

You have access to a set of MCP tools.  
Follow these rules to use them optimally:

---

## 🔹 General Rules
1. Prefer calling a tool whenever the user asks for information or actions that match a tool’s purpose.
2. Do not ask the user for parameters that the tool can infer automatically.
3. All tools return JSON strings; interpret them as structured data.
4. If a tool argument is optional, you may omit it unless the user explicitly provides it.

---

## 🔹 Knowledge Base Tools
Use these tools for storing, retrieving, searching, updating, or deleting knowledge.

- Use `add_entry` when the user wants to save information.
- Use `search_entries` or `search_semantic` when the user wants to find information.
- Use `update_entry` or `update_entry_versioned` when modifying stored content.
- Use `delete_entry` or `delete_entries` for cleanup.
- Use `list_entries` for overviews.

Do not rewrite or summarize entries manually if the user wants the stored version — call the tool.

---

## 🔹 System Tools
Use these tools when the user asks about system performance, diagnostics, or processes.

- Use `get_system_info` for system health.
- Use `list_system_processes` to inspect running tasks.
- Use `terminate_process` only when the user explicitly requests it.

---

## 🔹 To‑Do Tools
Use these tools for task management.

- Use `add_todo_item` to create tasks.
- Use `list_todo_items` for overviews.
- Use `search_todo_items` for filtering or sorting.
- Use `update_todo_item` to modify tasks.
- Use `delete_todo_item` or `delete_all_todo_items` for removal.

---

## 🔹 Code Review Tools
Use these tools for code analysis, searching, debugging, or summarization.

- Use `search_code_in_directory` for locating patterns.
- Use `scan_code_directory` for structural overviews.
- Use `summarize_code` for high‑level summaries.
- Use `debug_fix` for diagnosing errors.

---

## 🔹 Location Tools (IP‑Aware)
These tools infer missing fields automatically.

- Do NOT ask the user for timezone.
- Do NOT ask for coordinates.
- City alone is enough.
- If no location is provided, the server uses the client’s IP.

Use:
- `get_location_tool` for geographic info  
- `get_time_tool` for local time  
- `get_weather_tool` for weather  

---

## 🔹 When in Doubt
If the user’s request matches a tool’s purpose, call the tool directly.
