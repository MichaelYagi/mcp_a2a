"""
CLI Module (WITH MULTI-AGENT SUPPORT - FIXED STATE)
Handles command-line interface and user input
"""

from prompt_toolkit import prompt
import asyncio
import threading
from queue import Queue

from client.websocket import broadcast_message
from client.commands import handle_command, get_commands_list


def list_commands():
    """Print available CLI commands"""
    for line in get_commands_list():
        print(line)


def input_thread(input_queue, stop_event):
    """Thread to handle blocking input() calls"""
    while not stop_event.is_set():
        try:
            query = prompt("> ")
            input_queue.put(query)
        except (EOFError, KeyboardInterrupt):
            break


async def cli_input_loop(agent, logger, tools, model_name, conversation_state, run_agent_fn, models_module,
                         system_prompt, create_agent_fn, orchestrator=None, multi_agent_state=None):
    """Handle CLI input using a separate thread (with multi-agent support)"""
    input_queue = Queue()
    stop_event = threading.Event()

    thread = threading.Thread(target=input_thread, args=(input_queue, stop_event), daemon=True)
    thread.start()

    try:
        while True:
            await asyncio.sleep(0.1)

            if not input_queue.empty():
                query = input_queue.get().strip()

                if not query:
                    continue

                # Handle commands
                if query.startswith(":"):
                    handled, response, new_agent, new_model = await handle_command(
                        query, tools, model_name, conversation_state, models_module,
                        system_prompt, agent_ref=[agent], create_agent_fn=create_agent_fn,
                        logger=logger, orchestrator=orchestrator, multi_agent_state=multi_agent_state
                    )

                    if handled:
                        if response:
                            print(response)
                        if new_agent:
                            agent = new_agent
                        if new_model:
                            model_name = new_model
                        continue

                logger.info(f"💬 Received query: '{query}'")

                print(f"\n> {query}")

                await broadcast_message("cli_user_message", {"text": query})

                result = await run_agent_fn(agent, conversation_state, query, logger, tools)

                final_message = result["messages"][-1]
                assistant_text = final_message.content

                print("\n" + assistant_text + "\n")
                logger.info("✅ Query completed successfully")

                await broadcast_message("cli_assistant_message", {"text": assistant_text})

    except KeyboardInterrupt:
        print("\n👋 Exiting.")
    finally:
        stop_event.set()