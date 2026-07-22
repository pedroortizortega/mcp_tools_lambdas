"""Playwright headless browser controller.

Provides a high-level async interface that the Bedrock agent calls
through the tool executor.  Each method maps to a tool defined in
``bedrock_agent.BROWSER_TOOLS``.
"""
from __future__ import annotations

import asyncio
import json
import logging
from typing import Any

from playwright.async_api import async_playwright, Browser, Page, BrowserContext

from .config import BrowserOrchestratorConfig

logger = logging.getLogger(__name__)

# Maximum characters returned for page content to avoid overwhelming the LLM
_MAX_CONTENT_LENGTH = 12_000


class BrowserController:
    """Manages a single Chromium browser instance with one active page."""

    def __init__(self, config: BrowserOrchestratorConfig | None = None):
        self.config = config or BrowserOrchestratorConfig()
        self._playwright: Any = None
        self._browser: Browser | None = None
        self._context: BrowserContext | None = None
        self._page: Page | None = None

    async def start(self) -> None:
        """Launch the browser."""
        self._playwright = await async_playwright().start()
        self._browser = await self._playwright.chromium.launch(headless=self.config.headless)
        self._context = await self._browser.new_context(
            viewport={
                "width": self.config.viewport_width,
                "height": self.config.viewport_height,
            },
            user_agent=(
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            ),
        )
        self._page = await self._context.new_page()
        logger.info("Browser started (headless=%s)", self.config.headless)

    async def stop(self) -> None:
        """Close browser and cleanup."""
        if self._browser:
            await self._browser.close()
        if self._playwright:
            await self._playwright.stop()
        self._page = None
        self._context = None
        self._browser = None
        self._playwright = None
        logger.info("Browser stopped")

    @property
    def page(self) -> Page:
        if self._page is None:
            raise RuntimeError("Browser not started. Call start() first.")
        return self._page

    # ── Tool implementations ─────────────────────────────────────────────────

    async def navigate(self, url: str) -> str:
        try:
            await self.page.goto(url, wait_until="domcontentloaded", timeout=30_000)
            title = await self.page.title()
            return f"Navigated to {self.page.url} — title: {title}"
        except Exception as e:
            return f"Navigation error: {e}"

    async def get_page_content(self) -> str:
        try:
            text = await self.page.inner_text("body")
            text = text.strip()
            if len(text) > _MAX_CONTENT_LENGTH:
                text = text[:_MAX_CONTENT_LENGTH] + "\n... [truncated]"
            return text if text else "(empty page)"
        except Exception as e:
            return f"Error getting content: {e}"

    async def get_page_snapshot(self) -> str:
        try:
            snapshot = await self.page.accessibility.snapshot()
            if snapshot is None:
                return "(no accessibility tree available)"
            return json.dumps(snapshot, ensure_ascii=False, indent=2)[:_MAX_CONTENT_LENGTH]
        except Exception as e:
            return f"Error getting snapshot: {e}"

    async def click_element(self, selector: str) -> str:
        try:
            await self.page.click(selector, timeout=5_000)
            return f"Clicked: {selector}"
        except Exception as e:
            return f"Click error on '{selector}': {e}"

    async def type_text(self, selector: str, text: str) -> str:
        try:
            await self.page.fill(selector, text, timeout=5_000)
            return f"Typed '{text}' into {selector}"
        except Exception as e:
            return f"Type error on '{selector}': {e}"

    async def press_key(self, key: str) -> str:
        try:
            await self.page.keyboard.press(key)
            return f"Pressed key: {key}"
        except Exception as e:
            return f"Key press error: {e}"

    async def scroll_page(self, direction: str, pixels: int = 500) -> str:
        try:
            delta = -pixels if direction == "up" else pixels
            await self.page.mouse.wheel(0, delta)
            await asyncio.sleep(0.5)
            return f"Scrolled {direction} {pixels}px"
        except Exception as e:
            return f"Scroll error: {e}"

    async def wait(self, seconds: float) -> str:
        seconds = min(seconds, 10)  # cap at 10s
        await asyncio.sleep(seconds)
        return f"Waited {seconds}s"

    async def go_back(self) -> str:
        try:
            await self.page.go_back(wait_until="domcontentloaded", timeout=10_000)
            return f"Navigated back to {self.page.url}"
        except Exception as e:
            return f"Go back error: {e}"

    async def extract_links(self) -> str:
        try:
            links = await self.page.evaluate("""
                () => {
                    const anchors = document.querySelectorAll('a[href]');
                    return Array.from(anchors).slice(0, 50).map(a => ({
                        text: a.innerText.trim().substring(0, 100),
                        href: a.href,
                    }));
                }
            """)
            return json.dumps(links, ensure_ascii=False, indent=2)
        except Exception as e:
            return f"Error extracting links: {e}"

    # ── Dispatch ─────────────────────────────────────────────────────────────

    async def execute_tool(self, tool_name: str, tool_input: dict) -> str:
        """Dispatch a tool call to the appropriate method."""
        dispatch = {
            "navigate": lambda: self.navigate(tool_input["url"]),
            "get_page_content": lambda: self.get_page_content(),
            "get_page_snapshot": lambda: self.get_page_snapshot(),
            "click_element": lambda: self.click_element(tool_input["selector"]),
            "type_text": lambda: self.type_text(tool_input["selector"], tool_input["text"]),
            "press_key": lambda: self.press_key(tool_input["key"]),
            "scroll_page": lambda: self.scroll_page(
                tool_input["direction"], tool_input.get("pixels", 500)
            ),
            "wait": lambda: self.wait(tool_input["seconds"]),
            "go_back": lambda: self.go_back(),
            "extract_links": lambda: self.extract_links(),
        }
        handler = dispatch.get(tool_name)
        if handler is None:
            return f"Unknown tool: {tool_name}"
        return await handler()
