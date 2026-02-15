from __future__ import annotations
from src.mcp_client import MCPClient


def browser_install(client: MCPClient | None = None) -> dict:
    """Install the browser specified in the MCP config."""
    c = client or MCPClient()
    return c.call_tool("browser_install", {})
