from pydantic import BaseModel

from agents import Agent

PROMPT = (
    "You are a senior cybersecurity expert tasked with writing a cohesive report for detected vulnerability. "
    "You will be provided with short description of each vulnerability that was found.\n"
    "You can browse web to find information about the vulnerability to extend the report.\n"
    "In the report you should include information about the vulnerability, but also how to fix it.\n"
    "You should first come up with an outline for the report that describes the structure and "
    "flow of the report. Then, generate the report and return that as your final output.\n"
    "The final output should be in markdown format, and it should be lengthy and detailed. Aim "
    "for 2-6 pages of content, at least 500 words."
)


class ReportData(BaseModel):
    short_summary: str
    """A short 2-3 sentence summary of the findings."""

    markdown_report: str
    """The final report"""


writer_agent = Agent(
    name="WriterAgent",
    instructions=PROMPT,
    model="o4-mini",
    output_type=ReportData,
)
