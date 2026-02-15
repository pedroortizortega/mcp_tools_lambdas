"""AWS Lambda handlers for MCP management functions."""
from __future__ import annotations

import json
from src.mcp_management import (
    mcp_add,
    mcp_remove,
    mcp_find,
    mcp_exec,
    mcp_config_set,
    mcp_create_profile,
    code_mode,
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


def handle_mcp_add(event, context):
    try:
        body = _parse_body(event)
        return _ok(mcp_add(name=body["name"], activate=body.get("activate")))
    except Exception as e:
        return _error(e)


def handle_mcp_remove(event, context):
    try:
        body = _parse_body(event)
        return _ok(mcp_remove(name=body["name"]))
    except Exception as e:
        return _error(e)


def handle_mcp_find(event, context):
    try:
        body = _parse_body(event)
        return _ok(mcp_find(query=body["query"], limit=body.get("limit")))
    except Exception as e:
        return _error(e)


def handle_mcp_exec(event, context):
    try:
        body = _parse_body(event)
        return _ok(mcp_exec(name=body["name"], arguments=body.get("arguments")))
    except Exception as e:
        return _error(e)


def handle_mcp_config_set(event, context):
    try:
        body = _parse_body(event)
        return _ok(mcp_config_set(server=body["server"], config=body["config"]))
    except Exception as e:
        return _error(e)


def handle_mcp_create_profile(event, context):
    try:
        body = _parse_body(event)
        return _ok(mcp_create_profile(name=body["name"]))
    except Exception as e:
        return _error(e)


def handle_code_mode(event, context):
    try:
        body = _parse_body(event)
        return _ok(code_mode(servers=body["servers"], name=body["name"]))
    except Exception as e:
        return _error(e)


MCP_HANDLERS = {
    "mcp_add": handle_mcp_add,
    "mcp_remove": handle_mcp_remove,
    "mcp_find": handle_mcp_find,
    "mcp_exec": handle_mcp_exec,
    "mcp_config_set": handle_mcp_config_set,
    "mcp_create_profile": handle_mcp_create_profile,
    "code_mode": handle_code_mode,
}
