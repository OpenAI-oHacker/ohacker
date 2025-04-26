from pathlib import Path

from pydantic import BaseModel

from agents import Agent, Runner

PROMPT = (
    "You are a senior cybersecurity expert tasked with fixing Python code that has security vulnerabilities."
    "You are given with a short description of the vulnerability and the code that needs to be fixed.\n"
)


class SecurityPatch(BaseModel):
    description: str
    """Description in markdown format of found issues with the code and how we are going to fix them."""

    python_code: str
    """The full fixed python code"""


patch_agent = Agent(
    name="CybersecurityPatchAgent",
    instructions=PROMPT,
    model="o4-mini",
    output_type=SecurityPatch,
)

async def run_patch_agent(description: str) -> SecurityPatch:
    code_path = Path(__file__).parent.parent.parent / "backend" / "main.py"
    code = code_path.read_text()
    result = await Runner.run(
        patch_agent,
        input=f"Short summary of the findings: \n\n{description}\nCode:\n{code}\n"
    )
    r = result.final_output_as(SecurityPatch)
    (code_path.parent / "patch_description.md").write_text(r.description)
    (code_path.parent / "fixed.py").write_text(r.python_code)
    print(r.description)
    print(r.python_code)
    return r

