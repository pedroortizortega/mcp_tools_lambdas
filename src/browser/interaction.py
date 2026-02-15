from __future__ import annotations
from src.mcp_client import MCPClient


def browser_click(
    element: str,
    ref: str,
    button: str | None = None,
    double_click: bool | None = None,
    modifiers: list[str] | None = None,
    client: MCPClient | None = None,
) -> dict:
    """Click an element on the page.

    Args:
        element: Human-readable element description.
        ref: Exact target element reference from the page snapshot.
        button: 'left', 'right', or 'middle'. Defaults to 'left'.
        double_click: Whether to perform a double click.
        modifiers: Modifier keys like 'Alt', 'Control', 'Shift', 'Meta'.
    """
    c = client or MCPClient()
    args: dict = {"element": element, "ref": ref}
    if button is not None:
        args["button"] = button
    if double_click is not None:
        args["doubleClick"] = double_click
    if modifiers is not None:
        args["modifiers"] = modifiers
    return c.call_tool("browser_click", args)


def browser_type(
    element: str,
    ref: str,
    text: str,
    slowly: bool | None = None,
    submit: bool | None = None,
    client: MCPClient | None = None,
) -> dict:
    """Type text into an editable element.

    Args:
        element: Human-readable element description.
        ref: Exact target element reference.
        text: Text to type.
        slowly: Type one character at a time to trigger key handlers.
        submit: Press Enter after typing.
    """
    c = client or MCPClient()
    args: dict = {"element": element, "ref": ref, "text": text}
    if slowly is not None:
        args["slowly"] = slowly
    if submit is not None:
        args["submit"] = submit
    return c.call_tool("browser_type", args)


def browser_hover(
    element: str,
    ref: str,
    client: MCPClient | None = None,
) -> dict:
    """Hover over an element on the page."""
    c = client or MCPClient()
    return c.call_tool("browser_hover", {"element": element, "ref": ref})


def browser_drag(
    start_element: str,
    start_ref: str,
    end_element: str,
    end_ref: str,
    client: MCPClient | None = None,
) -> dict:
    """Drag and drop between two elements."""
    c = client or MCPClient()
    return c.call_tool("browser_drag", {
        "startElement": start_element,
        "startRef": start_ref,
        "endElement": end_element,
        "endRef": end_ref,
    })


def browser_fill_form(
    fields: list[dict],
    client: MCPClient | None = None,
) -> dict:
    """Fill multiple form fields.

    Args:
        fields: List of dicts with keys: name, ref, type, value.
                type is one of: 'textbox', 'checkbox', 'radio', 'combobox', 'slider'.
    """
    c = client or MCPClient()
    return c.call_tool("browser_fill_form", {"fields": fields})


def browser_select_option(
    element: str,
    ref: str,
    values: list[str],
    client: MCPClient | None = None,
) -> dict:
    """Select an option in a dropdown."""
    c = client or MCPClient()
    return c.call_tool("browser_select_option", {
        "element": element,
        "ref": ref,
        "values": values,
    })


def browser_press_key(
    key: str,
    client: MCPClient | None = None,
) -> dict:
    """Press a key on the keyboard (e.g. 'ArrowLeft', 'Enter', 'a')."""
    c = client or MCPClient()
    return c.call_tool("browser_press_key", {"key": key})
