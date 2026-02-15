from __future__ import annotations
from src.mcp_client import MCPClient


def browser_navigate(url: str, client: MCPClient | None = None) -> dict:
    """Navigate the browser to the given URL."""
    c = client or MCPClient()
    return c.call_tool("browser_navigate", {"url": url})


def browser_navigate_back(client: MCPClient | None = None) -> dict:
    """Go back to the previous page."""
    c = client or MCPClient()
    return c.call_tool("browser_navigate_back", {})


def browser_close(client: MCPClient | None = None) -> dict:
    """Close the current browser page."""
    c = client or MCPClient()
    return c.call_tool("browser_close", {})


def browser_tabs(
    action: str,
    index: int | None = None,
    client: MCPClient | None = None,
) -> dict:
    """List, create, close, or select a browser tab.

    Args:
        action: One of 'list', 'new', 'close', 'select'.
        index: Tab index, used for close/select.
    """
    c = client or MCPClient()
    args: dict = {"action": action}
    if index is not None:
        args["index"] = index
    return c.call_tool("browser_tabs", args)
