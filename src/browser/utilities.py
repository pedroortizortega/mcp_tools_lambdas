from __future__ import annotations
from src.mcp_client import MCPClient


def browser_console_messages(
    only_errors: bool | None = None,
    client: MCPClient | None = None,
) -> dict:
    """Return all console messages from the page."""
    c = client or MCPClient()
    args: dict = {}
    if only_errors is not None:
        args["onlyErrors"] = only_errors
    return c.call_tool("browser_console_messages", args)


def browser_network_requests(client: MCPClient | None = None) -> dict:
    """Return all network requests since loading the page."""
    c = client or MCPClient()
    return c.call_tool("browser_network_requests", {})


def browser_wait_for(
    text: str | None = None,
    text_gone: str | None = None,
    time: float | None = None,
    client: MCPClient | None = None,
) -> dict:
    """Wait for text to appear/disappear or a specified time to pass.

    Args:
        text: Text to wait for.
        text_gone: Text to wait to disappear.
        time: Time to wait in seconds.
    """
    c = client or MCPClient()
    args: dict = {}
    if text is not None:
        args["text"] = text
    if text_gone is not None:
        args["textGone"] = text_gone
    if time is not None:
        args["time"] = time
    return c.call_tool("browser_wait_for", args)


def browser_handle_dialog(
    accept: bool,
    prompt_text: str | None = None,
    client: MCPClient | None = None,
) -> dict:
    """Handle a browser dialog (alert, confirm, prompt).

    Args:
        accept: Whether to accept the dialog.
        prompt_text: Text for prompt dialogs.
    """
    c = client or MCPClient()
    args: dict = {"accept": accept}
    if prompt_text is not None:
        args["promptText"] = prompt_text
    return c.call_tool("browser_handle_dialog", args)


def browser_file_upload(
    paths: list[str] | None = None,
    client: MCPClient | None = None,
) -> dict:
    """Upload one or multiple files. If paths is omitted, the file chooser is cancelled."""
    c = client or MCPClient()
    args: dict = {}
    if paths is not None:
        args["paths"] = paths
    return c.call_tool("browser_file_upload", args)
