"""
Metrics Module
Tracks performance metrics for MCP components
"""

from collections import defaultdict

metrics = {
    "agent_runs": 0,
    "agent_errors": 0,
    "agent_times": [],  # list of durations in seconds
    "llm_calls": 0,
    "llm_errors": 0,
    "llm_times": [],  # list of durations
    "tool_calls": defaultdict(int),  # tool_name: count
    "tool_errors": defaultdict(int),  # tool_name: count
    "tool_times": defaultdict(list),  # tool_name: [durations]
}

def prepare_metrics():
    """Prepare metrics data for broadcasting, with computations"""
    tool_total_calls = sum(metrics["tool_calls"].values())
    tool_total_errors = sum(metrics["tool_errors"].values())
    total_errors = metrics["agent_errors"] + metrics["llm_errors"] + tool_total_errors
    agent_error_rate = (metrics["agent_errors"] / metrics["agent_runs"] * 100) if metrics["agent_runs"] > 0 else 0

    agent_avg_time = sum(metrics["agent_times"]) / len(metrics["agent_times"]) if metrics["agent_times"] else 0
    llm_avg_time = sum(metrics["llm_times"]) / len(metrics["llm_times"]) if metrics["llm_times"] else 0
    tool_avg_times = {k: sum(v) / len(v) if v else 0 for k, v in metrics["tool_times"].items()}

    # Limit time series to last 100 for graphs
    recent_agent_times = metrics["agent_times"][-100:]
    recent_llm_times = metrics["llm_times"][-100:]
    recent_tool_times = {k: v[-100:] for k, v in metrics["tool_times"].items()}

    return {
        "agent": {
            "runs": metrics["agent_runs"],
            "errors": metrics["agent_errors"],
            "error_rate": round(agent_error_rate, 2),
            "avg_time": round(agent_avg_time, 2),
            "times": recent_agent_times,
        },
        "llm": {
            "calls": metrics["llm_calls"],
            "errors": metrics["llm_errors"],
            "avg_time": round(llm_avg_time, 2),
            "times": recent_llm_times,
        },
        "tools": {
            "total_calls": tool_total_calls,
            "total_errors": tool_total_errors,
            "per_tool": {
                name: {
                    "calls": metrics["tool_calls"][name],
                    "errors": metrics["tool_errors"][name],
                    "avg_time": round(tool_avg_times.get(name, 0), 2),
                    "times": recent_tool_times.get(name, [])
                } for name in metrics["tool_calls"]
            }
        },
        "overall_errors": total_errors
    }