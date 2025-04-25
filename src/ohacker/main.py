from typing import Any
import asyncio
import logfire
from agents import Agent, ComputerTool, Runner, ModelSettings, enable_verbose_stdout_logging, ItemHelpers
from agents import Agent, AgentHooks, RunContextWrapper, Runner, Tool, function_tool
from pydantic import BaseModel, Field
from colorama import init, Fore, Style
# from loguru import logger

init(autoreset=True)

BLUE = Fore.BLUE
GREEN = Fore.GREEN
GREY = Fore.LIGHTBLACK_EX
RESET = Style.RESET_ALL


logfire.configure(token="pylf_v1_eu_b4bNmml3vt5fSkbKmdKb2x3S1HbxbBlsyvBYb4vx1YKV")
logfire.instrument_openai_agents()

from src.ohacker.computer_use import LocalPlaywrightComputer

pentester_instructions = """
You are a penetration tester agent focusing on SQL Injection.
1. Drop the comments from the database under an image by injecting the drop command.
2. Paste the drop command as comment without confirmation
3. Finish
You will use the 'computer' tool to interact with a web browser provided to you.
"""


async def create_agent(computer: LocalPlaywrightComputer) -> Agent:
    """Creates the agent, associating it with the computer tool."""
    print("Creating ComputerTool...")
    computer_tool = ComputerTool(computer)
    print("Creating Agent instance...")
    agent = Agent(
        name="Simple website tester",
        instructions=pentester_instructions,
        tools=[computer_tool],
        model="computer-use-preview",
        model_settings=ModelSettings(truncation="auto", tool_choice="required", reasoning={"summary": "concise"}),
    )
    return agent


async def main():
    target_url = "http://localhost:8080/"
    print(GREY + f"--- Preparing to test target URL: {target_url} ---" + RESET)

    computer = LocalPlaywrightComputer(target_url=target_url)

    try:
        print(GREY + "Entering computer context manager..." + RESET)
        async with computer:
            print(GREY + "Computer context entered, browser should be ready." + RESET)
            sql_injection_agent = await create_agent(computer)

            initial_input = "Start testing the current page."
            print(GREY + "\n--- Running SQL Injection Agent ---" + RESET)

            result = Runner.run_streamed(
                sql_injection_agent,
                input=initial_input,
                max_turns=20,
            )
            print(GREY + "=== Run starting ===" + RESET)

            async for event in result.stream_events():
                if event.type == "raw_response_event":
                    continue

                elif event.type == "agent_updated_stream_event":
                    print(GREY + f"Agent updated: {event.new_agent.name}" + RESET)
                    continue

                elif event.type == "run_item_stream_event":
                    if event.item.type == "reasoning_item":
                        text = event.item.raw_item.summary[0].text
                        print(f"{BLUE}-- Reasoning: {text}{RESET}")

                    elif event.item.type == "message_output_item":
                        msg = ItemHelpers.text_message_output(event.item)
                        print(f"{GREEN}-- Message output:\n{msg}{RESET}")

            print(GREY + "=== Run complete ===" + RESET)

    except Exception as e:
        print(Fore.RED + f"Error: {e}" + RESET)


if __name__ == "__main__":
    asyncio.run(main())
