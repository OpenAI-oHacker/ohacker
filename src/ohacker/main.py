from typing import Any
import asyncio
import logfire
from agents import Agent, ComputerTool, Runner, ModelSettings, enable_verbose_stdout_logging, ItemHelpers
from agents import Agent, AgentHooks, RunContextWrapper, Runner, Tool, function_tool
from pydantic import BaseModel, Field
# from loguru import logger


# enable_verbose_stdout_logging()


# configure logfire
logfire.configure(token="pylf_v1_eu_b4bNmml3vt5fSkbKmdKb2x3S1HbxbBlsyvBYb4vx1YKV")
logfire.instrument_openai_agents()

from src.ohacker.computer_use import LocalPlaywrightComputer

pentester_instructions = """
You are a basic penetration tester agent focusing on SQL Injection.
Drop the comments from the database under an image by injecting the drop command.
Observe whether the attempt was successful.
You will use the 'computer' tool to interact with a web browser provided to you.
At the end, output the detailed summary of your results, whether the injection was correct and what you did.
"""


# class CustomAgentHooks(AgentHooks):
#     def __init__(self, display_name: str):
#         self.event_counter = 0
#         self.display_name = display_name

#     async def on_tool_end(self, context: RunContextWrapper, agent: Agent, tool: Tool, result: str) -> None:
#         self.event_counter += 1
#         print(f"### ({self.display_name}) {self.event_counter}: Agent {agent.name} ended tool {tool.name}")


class SQLiReport(BaseModel):
    summary: str = Field(..., description="Overall summary of the SQL injection testing phase.")


async def create_agent(computer: LocalPlaywrightComputer) -> Agent:
    """Creates the agent, associating it with the computer tool."""
    print("Creating ComputerTool...")
    computer_tool = ComputerTool(computer)
    print("Creating Agent instance...")
    agent = Agent(
        name="Simple SQL Injection Tester",
        instructions=pentester_instructions,
        tools=[computer_tool],
        model="computer-use-preview",
        model_settings=ModelSettings(truncation="auto", tool_choice="required", reasoning={"summary": "concise"}),
        # hooks=CustomAgentHooks(display_name="Logs"),
    )
    return agent


async def main():
    # target_url = "https://www.bing.com/"
    # target_url = "http://127.0.0.1:8001/docs"
    target_url = "http://localhost:8080/"
    print(f"--- Preparing to test target URL: {target_url} ---")

    computer = LocalPlaywrightComputer(target_url=target_url)

    try:
        print("Entering computer context manager...")
        async with computer:
            print("Computer context entered, browser should be ready.")
            sql_injection_agent = await create_agent(computer)

            initial_input = "Start the SQL injection test on the current page."
            print("\n--- Running SQL Injection Agent ---")

            result = Runner.run_streamed(
                sql_injection_agent,
                input=initial_input,
                max_turns=20,
            )
            print("=== Run starting ===")

            async for event in result.stream_events():
                if event.type == "raw_response_event":
                    continue
                elif event.type == "agent_updated_stream_event":
                    print(f"Agent updated: {event.new_agent.name}")
                    continue
                elif event.type == "run_item_stream_event":
                    if event.item.type == "reasoning_item":
                        print(f"-- Reasoning: {event.item.raw_item.summary[0].text}")
                    elif event.item.type == "message_output_item":
                        print(f"-- Message output:\n {ItemHelpers.text_message_output(event.item)}")
                    else:
                        pass

            print("=== Run complete ===")

    except RuntimeError as e:
        print(f"\nRuntime Error during agent run or setup: {e}")
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")
        import traceback

        traceback.print_exc()
    finally:
        print("Exiting main try block (cleanup handled by async with).")


if __name__ == "__main__":
    print("Starting script...")
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nExecution interrupted by user.")
    finally:
        print("Script finished.")


# zadanie
# to zrobił
# wynik
# raport z opisem
