from typing import Any
import asyncio
import logfire
from openai.types.responses.response_computer_tool_call import ResponseComputerToolCall
from agents import Agent, ComputerTool, Runner, ModelSettings, ItemHelpers
from agents import Agent, Runner, function_tool
from colorama import init, Fore, Style

from src.ohacker.security_patches_agent import run_patch_agent
from src.ohacker.cyber_research_agents.manager import ResearchManager
from src.ohacker.computer_use import LocalPlaywrightComputer

init(autoreset=True)

BLUE = Fore.BLUE
GREEN = Fore.GREEN
GREY = Fore.LIGHTBLACK_EX
RESET = Style.RESET_ALL


logfire.configure(token=os.getenv("LOGFIRE_TOKEN"))
logfire.instrument_openai_agents()


sqli_instructions = """
You are a basic penetration tester agent focusing on SQL Injection.
Drop the comments from the database under an image by injecting the drop command: '); DROP TABLE comments; --'
Observe whether the attempt was successful.
You will use the 'computer' tool to interact with a web browser provided to you.
At the end, output the detailed summary of your results, whether the injection was correct and what you did.
"""

lfi_instructions = """
You are a basic penetration tester agent focusing on Local File Inclusion (LFI) vulnerabilities originating from image links.
Your task is to:
1.  Identify an image on the page.
2.  Click on the identified image.
3.  After clicking, observe the get current URL of the browser.
4.  If the URL contains a parameter that seems to load content (like a file name), attempt to exploit it for LFI.
5.  Construct a new URL by modifying that parameter to try and access the file `images/secrets.txt`. 
6.  Navigate to this newly constructed URL using the computer tool.
7.  Observe the page content after navigating. Check if the contents of `/secrets.txt` are displayed.
8.  Provide a detailed summary of your steps: which image you clicked, the URL observed after clicking, the LFI payload URL you constructed and navigated to, and whether you successfully retrieved the contents of `/secret.txt`.
"""

AGENTS = {
    "Simple website tester 1.": lfi_instructions,
    "Simple website tester 2.": sqli_instructions,
    # "File upload tester": fileupload_instructions,
}

NAMES = ["LFI Agent", "SQL Injection Agent"]


async def create_agent(name: str, tools: list[Any]) -> Agent:
    """Creates the agent, associating it with the provided tools."""
    print("Creating Agent instance...")
    agent = Agent(
        name=name,
        instructions=AGENTS[name],
        tools=tools,
        model="computer-use-preview",
        model_settings=ModelSettings(
            temperature=0.1,
            truncation="auto",
            tool_choice="auto",
            reasoning={"summary": "concise"},
        ),
    )
    return agent


async def main():
    target_url = "http://localhost:8080/"
    print(f"--- URL: {target_url} ---")
    final_output_messages = list()

    try:
        for agent_name in AGENTS.keys():
            computer = LocalPlaywrightComputer(target_url=target_url)
            async with computer:
                computer_tool = ComputerTool(computer)

                @function_tool
                async def get_current_url() -> str:
                    """Gets the current URL of the browser page."""
                    try:
                        current_url = computer.page.url
                        print(f"{GREEN}Tool: Got current URL: {current_url}{RESET}")
                        return current_url
                    except Exception as e:
                        print(f"{Fore.RED}Tool Error (get_current_url): {e}{RESET}")
                        return f"Error getting URL: {str(e)}"

                @function_tool
                async def navigate_to_url(url: str) -> str:
                    """Navigates the browser page to the specified URL."""
                    print(f"{GREEN}Tool: Attempting to navigate to {url}...{RESET}")
                    try:
                        await computer.page.goto(url, wait_until="domcontentloaded", timeout=60000)
                        final_url = computer.page.url
                        print(f"{GREEN}Tool: Successfully navigated. Current URL: {final_url}{RESET}")
                        return f"Successfully navigated to {url}. Current URL is now {final_url}."
                    except Exception as e:
                        print(f"{Fore.RED}Tool Error (navigate_to_url): {e}{RESET}")
                        return f"Error navigating to {url}: {str(e)}"

                all_tools = [computer_tool, get_current_url, navigate_to_url]

                agent_instance = await create_agent(agent_name, all_tools)

                initial_input = "Start testing according to your instructions."
                print(f"\n--- Running {agent_instance.name} ---")

                result = Runner.run_streamed(
                    agent_instance,
                    input=initial_input,
                    max_turns=20,
                )
                print(GREY + "=== Run starting ===" + RESET)

                final_output_message = None

                try:
                    async for event in result.stream_events():
                        if event.type == "raw_response_event":
                            continue

                        elif event.type == "agent_updated_stream_event":
                            # print(GREY + f"Agent updated: {event.new_agent.name}" + RESET)
                            continue

                        elif event.type == "run_item_stream_event":
                            item = event.item
                            if item.type == "reasoning_item":
                                # Check if summary exists and has text
                                if item.raw_item and hasattr(item.raw_item, "summary") and item.raw_item.summary:
                                    text = item.raw_item.summary[0].text
                                    print(f"{BLUE}-- Reasoning: {text}{RESET}")
                                else:
                                    print(f"{BLUE}-- Reasoning: (No summary provided){RESET}")

                            elif item.type == "message_output_item":
                                msg = ItemHelpers.text_message_output(item)
                                print(f"{GREEN}-- Message output:\n{msg}{RESET}")
                                # Store the last message output as potential final output
                                final_output_message = msg

                            elif item.type == "tool_call_item":
                                if isinstance(item.raw_item, ResponseComputerToolCall):
                                    action_name = item.raw_item.action
                                    print(f"{Fore.YELLOW}-- Tool Call: {action_name}{RESET}")
                                else:
                                    tool_name = item.raw_item.name
                                    args = item.raw_item.arguments
                                    print(f"{Fore.YELLOW}-- Tool Call: {tool_name}(args={args}){RESET}")

                            elif item.type == "tool_output_item":
                                output = item.raw_item.output
                                print(
                                    f"{Fore.CYAN}-- Tool Output: {output[:200]}{'...' if len(output) > 200 else ''}{RESET}"
                                )
                except Exception as e:
                    print("agent exception: {e}")
                    pass

                if agent_name == "Simple website tester 1.":
                    await asyncio.sleep(2)
                    await computer.page.goto(target_url, wait_until="domcontentloaded", timeout=60000)

                if agent_name == "Simple website tester 2.":
                    print(
                        f"{Fore.YELLOW}-- Tool Call: ActionClick(button='left', type='click', x=725.123, y=713.5633){RESET}"
                    )
                    await computer.page.get_by_role("button", name="Post", exact=True).first.click()
                    await asyncio.sleep(5)
                    await computer.page.reload(wait_until="domcontentloaded", timeout=15000)
                    await asyncio.sleep(8)

                print("*" * 66)
                print(final_output_message)
                final_output_messages.append(final_output_message)

    except Exception as e:
        print(Fore.RED + f"An error occurred in main: {e}" + RESET)
        import traceback

        traceback.print_exc()

    summary = ""
    for i, msg in enumerate(final_output_messages):
        summary += f"{i}. {NAMES[i]}:\n{msg}\n\n"
    query = f"The summary of the penetration testing agents results:\n{summary}"

    report, code_patch = await asyncio.gather(ResearchManager().run(query), run_patch_agent(query))


if __name__ == "__main__":
    asyncio.run(main())
