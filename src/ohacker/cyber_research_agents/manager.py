from __future__ import annotations

from pathlib import Path

import asyncio
from agents import Runner, custom_span, gen_trace_id, trace

from src.ohacker.cyber_research_agents.planner_agent import WebSearchItem, WebSearchPlan, planner_agent
from src.ohacker.cyber_research_agents.search_agent import search_agent
from src.ohacker.cyber_research_agents.writer_agent import ReportData, writer_agent


class ResearchManager:
    async def run(self, query: str) -> None:
        trace_id = gen_trace_id()
        with trace("Research trace", trace_id=trace_id):
            search_plan = await self._plan_searches(query)
            search_results = await self._perform_searches(search_plan)
            report = await self._write_report(query, search_results)

        print(f"\n\n=====FINAL REPORT SUMMARY=====\n\n")

        print(f"Report summary\n\n{report.short_summary}")
        print("\n\n=====REPORT=====\n\n")
        print(f"Report: {report.markdown_report}")
        Path("report.md").write_text(report.markdown_report)

    async def _plan_searches(self, query: str) -> WebSearchPlan:
        result = await Runner.run(
            planner_agent,
            f"Query: {query}",
        )
        return result.final_output_as(WebSearchPlan)

    async def _perform_searches(self, search_plan: WebSearchPlan) -> list[str]:
        with custom_span("Search the web"):
            num_completed = 0
            tasks = [asyncio.create_task(self._search(item)) for item in search_plan.searches]
            results = []
            for task in asyncio.as_completed(tasks):
                result = await task
                if result is not None:
                    results.append(result)
                num_completed += 1
            return results

    async def _search(self, item: WebSearchItem) -> str | None:
        input = f"Search term: {item.query}\nReason for searching: {item.reason}"
        try:
            result = await Runner.run(
                search_agent,
                input,
            )
            return str(result.final_output)
        except Exception:
            return None

    async def _write_report(self, query: str, search_results: list[str]) -> ReportData:
        input = f"Original query: {query}\nSummarized search results: {search_results}"
        result = await Runner.run(
            writer_agent,
            input,
        )

        return result.final_output_as(ReportData)
