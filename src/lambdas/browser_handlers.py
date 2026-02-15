"""AWS Lambda handlers for all browser MCP functions.

Each handler:
  - Receives an API Gateway event with a JSON body.
  - Calls the corresponding browser function.
  - Returns a standard API Gateway response.
"""
from __future__ import annotations

import json
from src.browser import (
    browser_navigate,
    browser_navigate_back,
    browser_close,
    browser_tabs,
    browser_click,
    browser_type,
    browser_hover,
    browser_drag,
    browser_fill_form,
    browser_select_option,
    browser_press_key,
    browser_snapshot,
    browser_take_screenshot,
    browser_evaluate,
    browser_run_code,
    browser_resize,
    browser_console_messages,
    browser_network_requests,
    browser_wait_for,
    browser_handle_dialog,
    browser_file_upload,
    browser_install,
)


def _parse_body(event: dict) -> dict:
    body = event.get("body", "{}")
    if isinstance(body, str):
        return json.loads(body) if body else {}
    return body or {}


def _ok(result: dict) -> dict:
    return {"statusCode": 200, "body": json.dumps(result)}


def _error(e: Exception) -> dict:
    return {"statusCode": 500, "body": json.dumps({"error": str(e)})}


# ── Navigation ────────────────────────────────────────────────────────────────

def handle_browser_navigate(event, context):
    try:
        body = _parse_body(event)
        return _ok(browser_navigate(url=body["url"]))
    except Exception as e:
        return _error(e)


def handle_browser_navigate_back(event, context):
    try:
        return _ok(browser_navigate_back())
    except Exception as e:
        return _error(e)


def handle_browser_close(event, context):
    try:
        return _ok(browser_close())
    except Exception as e:
        return _error(e)


def handle_browser_tabs(event, context):
    try:
        body = _parse_body(event)
        return _ok(browser_tabs(action=body["action"], index=body.get("index")))
    except Exception as e:
        return _error(e)


# ── Interaction ───────────────────────────────────────────────────────────────

def handle_browser_click(event, context):
    try:
        body = _parse_body(event)
        return _ok(browser_click(
            element=body["element"],
            ref=body["ref"],
            button=body.get("button"),
            double_click=body.get("doubleClick"),
            modifiers=body.get("modifiers"),
        ))
    except Exception as e:
        return _error(e)


def handle_browser_type(event, context):
    try:
        body = _parse_body(event)
        return _ok(browser_type(
            element=body["element"],
            ref=body["ref"],
            text=body["text"],
            slowly=body.get("slowly"),
            submit=body.get("submit"),
        ))
    except Exception as e:
        return _error(e)


def handle_browser_hover(event, context):
    try:
        body = _parse_body(event)
        return _ok(browser_hover(element=body["element"], ref=body["ref"]))
    except Exception as e:
        return _error(e)


def handle_browser_drag(event, context):
    try:
        body = _parse_body(event)
        return _ok(browser_drag(
            start_element=body["startElement"],
            start_ref=body["startRef"],
            end_element=body["endElement"],
            end_ref=body["endRef"],
        ))
    except Exception as e:
        return _error(e)


def handle_browser_fill_form(event, context):
    try:
        body = _parse_body(event)
        return _ok(browser_fill_form(fields=body["fields"]))
    except Exception as e:
        return _error(e)


def handle_browser_select_option(event, context):
    try:
        body = _parse_body(event)
        return _ok(browser_select_option(
            element=body["element"],
            ref=body["ref"],
            values=body["values"],
        ))
    except Exception as e:
        return _error(e)


def handle_browser_press_key(event, context):
    try:
        body = _parse_body(event)
        return _ok(browser_press_key(key=body["key"]))
    except Exception as e:
        return _error(e)


# ── Page ──────────────────────────────────────────────────────────────────────

def handle_browser_snapshot(event, context):
    try:
        return _ok(browser_snapshot())
    except Exception as e:
        return _error(e)


def handle_browser_take_screenshot(event, context):
    try:
        body = _parse_body(event)
        return _ok(browser_take_screenshot(
            element=body.get("element"),
            ref=body.get("ref"),
            filename=body.get("filename"),
            full_page=body.get("fullPage"),
            image_type=body.get("type"),
        ))
    except Exception as e:
        return _error(e)


def handle_browser_evaluate(event, context):
    try:
        body = _parse_body(event)
        return _ok(browser_evaluate(
            function=body["function"],
            element=body.get("element"),
            ref=body.get("ref"),
        ))
    except Exception as e:
        return _error(e)


def handle_browser_run_code(event, context):
    try:
        body = _parse_body(event)
        return _ok(browser_run_code(code=body["code"]))
    except Exception as e:
        return _error(e)


def handle_browser_resize(event, context):
    try:
        body = _parse_body(event)
        return _ok(browser_resize(width=body["width"], height=body["height"]))
    except Exception as e:
        return _error(e)


# ── Utilities ─────────────────────────────────────────────────────────────────

def handle_browser_console_messages(event, context):
    try:
        body = _parse_body(event)
        return _ok(browser_console_messages(only_errors=body.get("onlyErrors")))
    except Exception as e:
        return _error(e)


def handle_browser_network_requests(event, context):
    try:
        return _ok(browser_network_requests())
    except Exception as e:
        return _error(e)


def handle_browser_wait_for(event, context):
    try:
        body = _parse_body(event)
        return _ok(browser_wait_for(
            text=body.get("text"),
            text_gone=body.get("textGone"),
            time=body.get("time"),
        ))
    except Exception as e:
        return _error(e)


def handle_browser_handle_dialog(event, context):
    try:
        body = _parse_body(event)
        return _ok(browser_handle_dialog(
            accept=body["accept"],
            prompt_text=body.get("promptText"),
        ))
    except Exception as e:
        return _error(e)


def handle_browser_file_upload(event, context):
    try:
        body = _parse_body(event)
        return _ok(browser_file_upload(paths=body.get("paths")))
    except Exception as e:
        return _error(e)


def handle_browser_install(event, context):
    try:
        return _ok(browser_install())
    except Exception as e:
        return _error(e)


# ── Handler registry ──────────────────────────────────────────────────────────

BROWSER_HANDLERS = {
    "browser_navigate": handle_browser_navigate,
    "browser_navigate_back": handle_browser_navigate_back,
    "browser_close": handle_browser_close,
    "browser_tabs": handle_browser_tabs,
    "browser_click": handle_browser_click,
    "browser_type": handle_browser_type,
    "browser_hover": handle_browser_hover,
    "browser_drag": handle_browser_drag,
    "browser_fill_form": handle_browser_fill_form,
    "browser_select_option": handle_browser_select_option,
    "browser_press_key": handle_browser_press_key,
    "browser_snapshot": handle_browser_snapshot,
    "browser_take_screenshot": handle_browser_take_screenshot,
    "browser_evaluate": handle_browser_evaluate,
    "browser_run_code": handle_browser_run_code,
    "browser_resize": handle_browser_resize,
    "browser_console_messages": handle_browser_console_messages,
    "browser_network_requests": handle_browser_network_requests,
    "browser_wait_for": handle_browser_wait_for,
    "browser_handle_dialog": handle_browser_handle_dialog,
    "browser_file_upload": handle_browser_file_upload,
    "browser_install": handle_browser_install,
}
