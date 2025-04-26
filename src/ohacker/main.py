from typing import Any
import asyncio
import logfire
from agents import Agent, ComputerTool, Runner, ModelSettings, enable_verbose_stdout_logging, ItemHelpers
from agents import Agent, AgentHooks, RunContextWrapper, Runner, Tool, function_tool
from pydantic import BaseModel, Field
from colorama import init, Fore, Style

from src.ohacker.cyber_research_agents.manager import ResearchManager
# from loguru import logger
from src.ohacker.computer_use import LocalPlaywrightComputer

init(autoreset=True)

BLUE = Fore.BLUE
GREEN = Fore.GREEN
GREY = Fore.LIGHTBLACK_EX
RESET = Style.RESET_ALL


logfire.configure(token="pylf_v1_eu_b4bNmml3vt5fSkbKmdKb2x3S1HbxbBlsyvBYb4vx1YKV")
logfire.instrument_openai_agents()


pentester_instructions = """
You are a basic penetration tester agent focusing on SQL Injection.
Drop the comments from the database under an image by injecting the drop command.
Observe whether the attempt was successful.
You will use the 'computer' tool to interact with a web browser provided to you.
At the end, output the detailed summary of your results, whether the injection was correct and what you did.
"""

lfi_instructions =  """
You are a basic penetration tester agent focusing on Local File Inclusion (LFI).
Identify a potentially vulnerable parameter in the web application (e.g., a file or page parameter in the URL).
Attempt to exploit this parameter using directory traversal techniques (e.g., '../') to read the '/secret.txt' file from the server's filesystem.
Click on the images to see if they are clickable. What does current url tell you?
Observe whether the contents of the file are displayed in the browser's response.
"""

AGENTS = {
    "Simple website tester": pentester_instructions,
    "LFI tester": lfi_instructions,
}

class GoToPageTool:
    """A tool that allows the agent to navigate to a specific URL."""

    def __init__(self, browser):
        self.browser = browser

    async def go_to_page(self, page):
        await self.browser.goto(self.url)
        return f"Navigated to {self.url}"

async def create_agent(name: str, computer: LocalPlaywrightComputer) -> Agent:
    """Creates the agent, associating it with the computer tool."""
    print("Creating ComputerTool...")
    computer_tool = ComputerTool(computer)
    print("Creating Agent instance...")
    agent = Agent(
        name=name,
        instructions=AGENTS[name],
        tools=[computer_tool],
        model="computer-use-preview",
        model_settings=ModelSettings(truncation="auto", tool_choice="required", reasoning={"summary": "concise"}),
    )
    return agent


async def main():
    target_url = "http://localhost:8080/"
    print(GREY + f"--- Preparing to test target URL: {target_url} ---" + RESET)

    try:
        for agent in AGENTS.keys():
            computer = LocalPlaywrightComputer(target_url=target_url)
            print(GREY + "Entering computer context manager..." + RESET)
            async with computer:
                print(GREY + "Computer context entered, browser should be ready." + RESET)
                agent = await create_agent(agent, computer)

                initial_input = "Start testing the current page."
                print(GREY + f"\n--- Running {agent} ---" + RESET)

                result = Runner.run_streamed(
                    agent,
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
                if agent == "Simple website tester":
                    await computer.page.click('button:has-text("Post")')

                print(GREY + "=== Run complete ===" + RESET)

    except Exception as e:
        print(Fore.RED + f"Error: {e}" + RESET)

    #TODO ERYK
    query = query = ("Short summary of the findings: \n\n"
             "1. Found a SQL injection vulnerability in the login form.\n"
             "2. Found a local file inclusion (LFI) vulnerability in the file upload feature.\n")
    await ResearchManager().run(query)



if __name__ == "__main__":
    asyncio.run(main())
