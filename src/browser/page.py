from __future__ import annotations
from src.mcp_client import MCPClient


def browser_snapshot(client: MCPClient | None = None) -> dict:
    """Capture accessibility snapshot of the current page."""
    c = client or MCPClient()
    return c.call_tool("browser_snapshot", {})


def browser_take_screenshot(
    element: str | None = None,
    ref: str | None = None,
    filename: str | None = None,
    full_page: bool | None = None,
    image_type: str | None = None,
    client: MCPClient | None = None,
) -> dict:
    """Take a screenshot of the current page or a specific element.

    Args:
        element: Human-readable element description.
        ref: Exact target element reference.
        filename: File name to save the screenshot to.
        full_page: Capture the full scrollable page.
        image_type: 'png' or 'jpeg'.
    """
    c = client or MCPClient()
    args: dict = {}
    if element is not None:
        args["element"] = element
    if ref is not None:
        args["ref"] = ref
    if filename is not None:
        args["filename"] = filename
    if full_page is not None:
        args["fullPage"] = full_page
    if image_type is not None:
        args["type"] = image_type
    return c.call_tool("browser_take_screenshot", args)


def browser_evaluate(
    function: str,
    element: str | None = None,
    ref: str | None = None,
    client: MCPClient | None = None,
) -> dict:
    """Evaluate a JavaScript expression on the page or element.

    Args:
        function: JS function like '() => { ... }' or '(element) => { ... }'.
        element: Human-readable element description.
        ref: Exact target element reference.
    """
    c = client or MCPClient()
    args: dict = {"function": function}
    if element is not None:
        args["element"] = element
    if ref is not None:
        args["ref"] = ref
    return c.call_tool("browser_evaluate", args)


def browser_run_code(
    code: str,
    client: MCPClient | None = None,
) -> dict:
    """Run a Playwright code snippet.

    Args:
        code: Playwright code that accesses the `page` object.
    """
    c = client or MCPClient()
    return c.call_tool("browser_run_code", {"code": code})


def browser_resize(
    width: int,
    height: int,
    client: MCPClient | None = None,
) -> dict:
    """Resize the browser window."""
    c = client or MCPClient()
    return c.call_tool("browser_resize", {"width": width, "height": height})
