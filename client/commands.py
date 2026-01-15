"""
Command Handlers for MCP Client
Compatible with existing CLI/WebSocket interfaces
"""


def get_commands_list():
    """Get list of available commands"""
    return [
        ":commands - List all available commands",
        ":stop - Stop current operation (ingestion, search, etc.)",
        ":stats - Show performance metrics",
        ":tools - List all available tools",
        ":tool <tool> - Get the tool description",
        ":model - View the current active model",
        ":model <model> - Use the model passed",
        ":models - List available models",
        ":multi on - Enable multi-agent mode",
        ":multi off - Disable multi-agent mode",
        ":multi status - Check multi-agent status",
        ":a2a on - Enable agent-to-agent mode",
        ":a2a off - Disable agent-to-agent mode",
        ":a2a status - Check A2A system status",
        ":health - Show agent health summary",
        ":health alerts - Show recent health alerts",
        ":health <agent> - Show health for specific agent",
        ":metrics - Show performance metrics summary",
        ":metrics comparative - Compare agent performance",
        ":metrics bottlenecks - Show performance bottlenecks",
        ":negotiations - Show negotiation statistics",
        ":routing - Show message routing statistics",
        ":routing queues - Show message queue status",
        ":clear history - Clear the chat history"
    ]


def list_commands():
    """Print all available commands"""
    print("\nAvailable Commands:")
    for cmd in get_commands_list():
        print(f"  {cmd}")


async def handle_a2a_commands(command: str, orchestrator):
    """
    Handle A2A-specific commands
    Returns result string or None if command not handled
    """
    if command == ":a2a on":
        if orchestrator:
            orchestrator.enable_a2a()
            return "✅ A2A mode enabled\n   Agents will communicate via messages\n   Use ':a2a status' to see agent status"
        return "❌ Multi-agent orchestrator not available"

    elif command == ":a2a off":
        if orchestrator:
            orchestrator.disable_a2a()
            return "🔗 A2A mode disabled\n   Falling back to multi-agent or single-agent mode"
        return "❌ Multi-agent orchestrator not available"

    elif command == ":a2a status":
        if not orchestrator:
            return "❌ Multi-agent orchestrator not available"

        status = orchestrator.get_a2a_status()
        if not status["enabled"]:
            return "A2A mode: DISABLED\n\nUse ':a2a on' to enable agent-to-agent communication"

        output = ["A2A mode: ENABLED", "=" * 60, ""]
        output.append("Agent Status:")
        output.append("-" * 60)

        for agent_name, agent_status in status["agents"].items():
            busy = "🔴 BUSY" if agent_status["is_busy"] else "🟢 IDLE"
            tools_count = len(agent_status["tools"])
            msgs = agent_status["messages_sent"]

            output.append(f"  {agent_name:15} {busy} | Tools: {tools_count:2} | Messages: {msgs:3}")

        output.append("")
        output.append(f"Message Queue: {status['message_queue_size']} messages")
        output.append("=" * 60)

        return "\n".join(output)

    return None


async def handle_multi_agent_commands(command: str, orchestrator, multi_agent_state):
    """
    Handle multi-agent commands
    Returns result string or None if command not handled
    """
    if command == ":multi on":
        if orchestrator:
            multi_agent_state["enabled"] = True
            return "✅ Multi-agent mode enabled\n   Complex queries will be broken down automatically"
        return "❌ Multi-agent orchestrator not available"

    elif command == ":multi off":
        if orchestrator:
            multi_agent_state["enabled"] = False
            return "🤖 Multi-agent mode disabled\n   Using single-agent execution"
        return "❌ Multi-agent orchestrator not available"

    elif command == ":multi status":
        if not orchestrator:
            return "❌ Multi-agent orchestrator not available"

        if multi_agent_state["enabled"]:
            return "Multi-agent mode: ENABLED\n   Complex queries are automatically distributed to specialized agents"
        else:
            return "Multi-agent mode: DISABLED\n   Use ':multi on' to enable"

    return None

async def handle_health_commands(command: str, orchestrator):
    """Handle health monitoring commands"""
    if not orchestrator or not orchestrator.health_monitor:
        return "❌ Health monitoring not available"

    if command == ":health":
        summary = orchestrator.health_monitor.get_health_summary()

        output = ["🏥 AGENT HEALTH SUMMARY", "=" * 60, ""]
        output.append(f"Status: {summary['status'].upper()}")
        output.append(f"Total Agents: {summary['total_agents']}")
        output.append(f"  Healthy: {summary['healthy']} | Degraded: {summary['degraded']}")
        output.append(f"  Unhealthy: {summary['unhealthy']} | Offline: {summary['offline']}")
        output.append("")
        output.append(f"Total Tasks: {summary['total_tasks']}")
        output.append(f"Total Errors: {summary['total_errors']}")
        output.append(f"Avg Response Time: {summary['avg_response_time']:.2f}s")
        output.append(f"Recent Alerts: {summary['recent_alerts']}")
        output.append("=" * 60)

        return "\n".join(output)

    elif command == ":health alerts":
        alerts = orchestrator.health_monitor.get_recent_alerts(limit=10)

        if not alerts:
            return "No recent alerts"

        output = ["🚨 RECENT ALERTS", "=" * 60]
        for alert in alerts:
            output.append(f"{alert.level.value.upper()} | {alert.agent_id}")
            output.append(f"  {alert.message}")
            output.append(f"  {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(alert.timestamp))}")
            output.append("")

        return "\n".join(output)

    elif command.startswith(":health "):
        agent_id = command[8:].strip()
        health = orchestrator.health_monitor.get_agent_health(agent_id)

        if not health:
            return f"❌ Agent {agent_id} not found"

        output = [f"🏥 HEALTH: {agent_id}", "=" * 60, ""]
        output.append(f"Status: {health.status.value.upper()}")
        output.append(f"Uptime: {health.uptime / 60:.1f} minutes")
        output.append(f"Tasks: {health.tasks_completed} completed, {health.tasks_failed} failed")
        output.append(f"Avg Response: {health.avg_response_time:.2f}s")
        output.append(f"Queue Size: {health.queue_size}")
        output.append(f"Error Count: {health.error_count}")

        if health.last_error:
            output.append(f"\nLast Error: {health.last_error}")

        return "\n".join(output)

    return None


async def handle_metrics_commands(command: str, orchestrator):
    """Handle performance metrics commands"""
    if not orchestrator or not orchestrator.performance_metrics:
        return "❌ Performance metrics not available"

    if command == ":metrics":
        report = orchestrator.performance_metrics.get_summary_report()
        return report

    elif command == ":metrics comparative":
        stats = orchestrator.performance_metrics.get_comparative_stats()

        output = ["📊 COMPARATIVE PERFORMANCE", "=" * 60, ""]

        if "overall" in stats:
            output.append("Overall Statistics:")
            output.append(f"  Avg Success Rate: {stats['overall']['avg_success_rate']:.1%}")
            output.append(f"  Avg Duration: {stats['overall']['avg_duration']:.2f}s")
            output.append(f"  Best Performer: {stats['overall']['best_performer']}")
            output.append(f"  Fastest Agent: {stats['overall']['fastest_agent']}")
            output.append("")

        output.append("Per-Agent:")
        for agent_id, data in stats['agents'].items():
            output.append(f"  {agent_id:15} | Success: {data['success_rate']:5.1%} | Avg: {data['avg_duration']:5.2f}s")

        return "\n".join(output)

    elif command == ":metrics bottlenecks":
        analysis = orchestrator.performance_metrics.get_bottleneck_analysis()

        if not analysis["bottlenecks"]:
            return "✅ No performance bottlenecks detected"

        output = ["⚠️  PERFORMANCE BOTTLENECKS", "=" * 60, ""]

        for bottleneck in analysis["bottlenecks"]:
            output.append(f"{bottleneck['agent_id']}:")
            for issue in bottleneck["issues"]:
                output.append(f"  - {issue}")
            output.append("")

        return "\n".join(output)

    return None

async def handle_negotiation_commands(command: str, orchestrator):
    """Handle negotiation commands"""
    if not orchestrator or not orchestrator.negotiation_engine:
        return "❌ Negotiation engine not available"

    if command == ":negotiations":
        stats = orchestrator.negotiation_engine.get_statistics()

        output = ["🤝 NEGOTIATION STATISTICS", "=" * 60, ""]
        output.append(f"Total Proposals: {stats['total_proposals']}")
        output.append(f"Accepted: {stats['accepted']}")
        output.append(f"Rejected: {stats['rejected']}")
        output.append(f"Expired: {stats['expired']}")
        output.append(f"Success Rate: {stats['success_rate']:.1%}")
        output.append(f"Active: {stats['active_negotiations']}")
        output.append("=" * 60)

        return "\n".join(output)

    return None

async def handle_routing_commands(command: str, orchestrator):
    """Handle message routing commands"""
    if not orchestrator or not orchestrator.message_router:
        return "❌ Message router not available"

    if command == ":routing":
        stats = orchestrator.message_router.get_routing_stats()

        output = ["📡 MESSAGE ROUTING STATISTICS", "=" * 60, ""]
        output.append(f"Total Routed: {stats['total_routed']}")
        output.append(f"Failed Routes: {stats['failed_routes']}")
        output.append(f"Retries: {stats['retries']}")
        output.append(f"Timeouts: {stats['timeouts']}")
        output.append(f"Pending: {stats['pending_messages']}")
        output.append(f"Completed: {stats['completed_messages']}")
        output.append("=" * 60)

        return "\n".join(output)

    elif command == ":routing queues":
        status = orchestrator.message_router.get_queue_status()

        if not status:
            return "No queues active"

        output = ["📬 MESSAGE QUEUE STATUS", "=" * 60, ""]

        for agent_id, queue_data in status.items():
            output.append(f"{agent_id}:")
            output.append(f"  Queue Size: {queue_data['queue_size']}")
            output.append(f"  Pending: {queue_data['pending']}")
            output.append(f"  Critical: {queue_data['priorities']['critical']}")
            output.append(f"  High: {queue_data['priorities']['high']}")
            output.append(f"  Normal: {queue_data['priorities']['normal']}")
            output.append("")

        return "\n".join(output)

    return None

def is_command(text: str) -> bool:
    """Check if text is a command"""
    return text.strip().startswith(":")


async def handle_command(
    command: str,
    tools,
    model_name,
    conversation_state,
    models_module,
    system_prompt,
    agent_ref=None,
    create_agent_fn=None,
    logger=None,
    orchestrator=None,
    multi_agent_state=None,
    a2a_state=None
):
    """
    Main command handler compatible with existing CLI/WebSocket interface

    Returns: (handled: bool, response: str, new_agent, new_model)
    """
    command = command.strip()

    # A2A commands
    if command.startswith(":a2a"):
        result = await handle_a2a_commands(command, orchestrator)
        if result:
            return (True, result, None, None)

    # Health commands
    if command.startswith(":health"):
        return await handle_health_commands(command, orchestrator)

    # Metrics commands
    if command.startswith(":metrics"):
        return await handle_metrics_commands(command, orchestrator)

    # Negotiation commands
    if command.startswith(":negotiations"):
        return await handle_negotiation_commands(command, orchestrator)

    # Routing commands
    if command.startswith(":routing"):
        return await handle_routing_commands(command, orchestrator)

    # Multi-agent commands
    if command.startswith(":multi"):
        result = await handle_multi_agent_commands(command, orchestrator, multi_agent_state)
        if result:
            return (True, result, None, None)

    # List commands
    if command == ":commands":
        result = "\n".join(get_commands_list())
        return (True, result, None, None)

    # Stop command
    if command == ":stop":
        from client.stop_signal import request_stop
        request_stop()
        return (True, "🛑 Stop signal sent - operations will halt at next checkpoint", None, None)

    # Stats command
    if command == ":stats":
        try:
            from client.metrics import prepare_metrics, format_metrics_summary
            metrics = prepare_metrics()
            summary = format_metrics_summary(metrics)
            return (True, summary, None, None)
        except ImportError:
            return (True, "📊 Stats system not available", None, None)

    # Tools command
    if command == ":tools":
        if tools:
            tool_list = "\n".join([f"  - {tool.name}: {tool.description}" for tool in tools])
            return (True, f"Available tools:\n{tool_list}", None, None)
        return (True, "No tools available", None, None)

    # Tool detail command
    if command.startswith(":tool "):
        tool_name = command[6:].strip()
        for tool in tools:
            if tool.name == tool_name:
                return (True, f"Tool: {tool.name}\n\n{tool.description}", None, None)
        return (True, f"Tool '{tool_name}' not found", None, None)

    # Model commands
    if command == ":model":
        return (True, f"Current model: {model_name}", None, None)

    if command == ":models":
        available = models_module.get_available_models()
        models_list = "\n".join([f"  {'→' if m == model_name else ' '} {m}" for m in available])
        return (True, f"Available models:\n{models_list}", None, None)

    if command.startswith(":model "):
        new_model = command[7:].strip()

        if logger:
            logger.info(f"Switching to model: {new_model}")

        new_agent = await models_module.switch_model(
            new_model,
            tools,
            logger,
            create_agent_fn
        )

        if new_agent is None:
            return (True, f"❌ Model '{new_model}' is not installed", None, None)

        return (True, f"✅ Switched to model: {new_model}", new_agent, new_model)

    # Clear history
    if command == ":clear history":
        conversation_state["messages"] = []
        return (True, "✅ Chat history cleared", None, None)

    # Command not recognized
    return (False, None, None, None)