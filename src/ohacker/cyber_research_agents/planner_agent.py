from pydantic import BaseModel

from agents import Agent

PROMPT = (
    "You are a helpful cybersecurity assistant. Given a description of the vulnerability of the website,"
    "come up with a set of web searches "
    "to perform to find the best recommendations to fix those vulnerabilities. Output between 5 and 10 terms to query for."
)


class WebSearchItem(BaseModel):
    reason: str
    "Your reasoning for why this search is important to the query."

    query: str
    "The search term to use for the web search."


class WebSearchPlan(BaseModel):
    searches: list[WebSearchItem]
    """A list of web searches to perform to find the best recommendations to fix those vulnerabilities."""


planner_agent = Agent(
    name="PlannerAgent",
    instructions=PROMPT,
    model="gpt-4o",
    output_type=WebSearchPlan,
)
