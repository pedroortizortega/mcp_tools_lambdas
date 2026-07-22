"""Orchestrator that connects Bedrock agent ↔ Playwright browser.

Flow:
  1. Receives (query, url) from the trigger endpoint.
  2. Starts a headless browser.
  3. Runs the Bedrock agentic loop where the LLM decides which
     browser tools to call to gather information.
  4. Returns the final synthesized answer.
"""
from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from typing import Any

from .bedrock_agent import BedrockAgent
from .browser_controller import BrowserController
from .config import BrowserOrchestratorConfig

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """\
You are a web research agent with access to a headless browser.
Your goal is to navigate to the provided URL and find the best, most
relevant information that answers the user's query.

Strategy:
1. First navigate to the URL provided.
2. Read the page content to understand what's there.
3. If the page has useful information, extract it.
4. If you need to search or navigate deeper (follow links, fill search
   forms, scroll), do so iteratively.
5. When you have enough information, provide a comprehensive answer
   in Spanish.

Rules:
- Be thorough but efficient — don't waste iterations.
- Always read page content after navigating.
- If a page is behind a login wall or requires authentication, report
  that you cannot access it.
- Summarize findings clearly with sources.
- Your final answer should be a well-structured summary of what you found.
"""


@dataclass
class SearchResult:
    """Holds the result of a search orchestration."""
    query: str
    url: str
    status: str = "pending"
    answer: str = ""
    iterations_used: int = 0
    error: str | None = None


class Orchestrator:
    """Bridges the Bedrock agent with the Playwright browser."""

    def __init__(self, config: BrowserOrchestratorConfig | None = None):
        self.config = config or BrowserOrchestratorConfig()

    async def search(self, query: str, url: str) -> SearchResult:
        """Run a full search session.

        Args:
            query: What to search for / extract.
            url: Starting URL to navigate to.

        Returns:
            SearchResult with the agent's findings.
        """
        result = SearchResult(query=query, url=url, status="in_progress")
        browser = BrowserController(self.config)
        agent = BedrockAgent(self.config)

        try:
            await browser.start()

            # Build the user message with query + url context
            user_message = (
                f"URL to investigate: {url}\n\n"
                f"Query: {query}\n\n"
                f"Navigate to the URL and find the best information to answer the query."
            )

            # The tool executor bridges sync Bedrock calls → async Playwright
            loop = asyncio.get_event_loop()

            def tool_executor(tool_name: str, tool_input: dict) -> str:
                future = asyncio.run_coroutine_threadsafe(
                    browser.execute_tool(tool_name, tool_input),
                    loop,
                )
                return future.result(timeout=60)

            # Run the Bedrock agent in a thread so async Playwright stays on main loop
            answer = await asyncio.to_thread(
                agent.run,
                system_prompt=SYSTEM_PROMPT,
                user_message=user_message,
                tool_executor=tool_executor,
            )

            result.answer = answer
            result.status = "completed"

        except Exception as exc:
            logger.exception("Orchestrator error")
            result.status = "error"
            result.error = str(exc)

        finally:
            await browser.stop()

        return result
