import asyncio

import logfire
from agents import (
    Agent,
    ComputerTool,
    ModelSettings,
    Runner,
    trace,
)

from ohacker.computer_use import LocalPlaywrightComputer

# configure logfire
logfire.configure(token="your-token")
logfire.instrument_openai_agents()


async def run_agent(query: str) -> dict:
    """
    Run a single agent with the given query.
    """
    async with LocalPlaywrightComputer() as computer:
        agent = Agent(
            name="Browser user",
            instructions="You are a helpful agent.",
            tools=[ComputerTool(computer)],
            # Use the computer using model, and set truncation to auto because its required
            model="computer-use-preview",
            model_settings=ModelSettings(truncation="auto"),
        )
        with trace(f"oHacker Computer Agent - {query}"):
            result = await Runner.run(agent, query, max_turns=20)
            print(f"Agent result for '{query}': {result.final_output}")
            return result.final_output


async def runner() -> None:
    """
    Agent runner.
    """
    # Define the search queries for each agent
    queries = [
        "Search for SF sports news and summarize.",
        "Search for Poland news and summarize.",
        "Search for France news and summarize.",
    ]

    # Run all agents in parallel
    results = await asyncio.gather(*[run_agent(query) for query in queries])

    # Print all results at the end
    for i, result in enumerate(results, 1):
        print(f"\nAgent {i} Final Result:\n{result}")


def main() -> None:
    """
    Main function.
    """
    asyncio.run(runner())


if __name__ == "__main__":
    main()
