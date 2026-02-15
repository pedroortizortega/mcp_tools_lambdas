from __future__ import annotations
from src.mcp_client import MCPClient


def mcp_add(
    name: str,
    activate: bool | None = None,
    client: MCPClient | None = None,
) -> dict:
    """Add a new MCP server to the session (must exist in catalog)."""
    c = client or MCPClient()
    args: dict = {"name": name}
    if activate is not None:
        args["activate"] = activate
    return c.call_tool("mcp-add", args)


def mcp_remove(name: str, client: MCPClient | None = None) -> dict:
    """Remove an MCP server from the registry."""
    c = client or MCPClient()
    return c.call_tool("mcp-remove", {"name": name})


def mcp_find(
    query: str,
    limit: int | None = None,
    client: MCPClient | None = None,
) -> dict:
    """Find MCP servers in the catalog by name, title, or description."""
    c = client or MCPClient()
    args: dict = {"query": query}
    if limit is not None:
        args["limit"] = limit
    return c.call_tool("mcp-find", args)


def mcp_exec(
    name: str,
    arguments: dict | None = None,
    client: MCPClient | None = None,
) -> dict:
    """Execute a tool that exists in the current session."""
    c = client or MCPClient()
    args: dict = {"name": name}
    if arguments is not None:
        args["arguments"] = arguments
    return c.call_tool("mcp-exec", args)


def mcp_config_set(
    server: str,
    config: dict,
    client: MCPClient | None = None,
) -> dict:
    """Set configuration for an MCP server."""
    c = client or MCPClient()
    return c.call_tool("mcp-config-set", {"server": server, "config": config})


def mcp_create_profile(name: str, client: MCPClient | None = None) -> dict:
    """Create or update a profile with the current gateway state."""
    c = client or MCPClient()
    return c.call_tool("mcp-create-profile", {"name": name})


def code_mode(
    servers: list[str],
    name: str,
    client: MCPClient | None = None,
) -> dict:
    """Create a JavaScript-enabled tool that combines multiple MCP server tools."""
    c = client or MCPClient()
    return c.call_tool("code-mode", {"servers": servers, "name": name})
