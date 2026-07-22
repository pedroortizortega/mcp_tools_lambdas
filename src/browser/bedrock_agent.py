"""AWS Bedrock Converse client with tool-use loop.

Wraps the Bedrock Runtime `converse` API so the agent can call browser
tools iteratively until it decides it has enough information.
"""
from __future__ import annotations

import json
import logging
from typing import Any

import boto3

from .config import BrowserOrchestratorConfig

logger = logging.getLogger(__name__)


# ── Tool definitions exposed to Bedrock ──────────────────────────────────────

BROWSER_TOOLS: list[dict] = [
    {
        "toolSpec": {
            "name": "navigate",
            "description": "Navigate the browser to a URL.",
            "inputSchema": {
                "json": {
                    "type": "object",
                    "properties": {"url": {"type": "string", "description": "URL to navigate to."}},
                    "required": ["url"],
                }
            },
        }
    },
    {
        "toolSpec": {
            "name": "get_page_content",
            "description": "Return the visible text content of the current page.",
            "inputSchema": {
                "json": {
                    "type": "object",
                    "properties": {},
                }
            },
        }
    },
    {
        "toolSpec": {
            "name": "get_page_snapshot",
            "description": "Return an accessibility snapshot (structured tree) of the current page.",
            "inputSchema": {
                "json": {
                    "type": "object",
                    "properties": {},
                }
            },
        }
    },
    {
        "toolSpec": {
            "name": "click_element",
            "description": "Click an element identified by CSS selector.",
            "inputSchema": {
                "json": {
                    "type": "object",
                    "properties": {"selector": {"type": "string", "description": "CSS selector of the element."}},
                    "required": ["selector"],
                }
            },
        }
    },
    {
        "toolSpec": {
            "name": "type_text",
            "description": "Type text into an input field identified by CSS selector.",
            "inputSchema": {
                "json": {
                    "type": "object",
                    "properties": {
                        "selector": {"type": "string", "description": "CSS selector of the input."},
                        "text": {"type": "string", "description": "Text to type."},
                    },
                    "required": ["selector", "text"],
                }
            },
        }
    },
    {
        "toolSpec": {
            "name": "press_key",
            "description": "Press a keyboard key (e.g. 'Enter', 'Tab', 'Escape').",
            "inputSchema": {
                "json": {
                    "type": "object",
                    "properties": {"key": {"type": "string", "description": "Key name."}},
                    "required": ["key"],
                }
            },
        }
    },
    {
        "toolSpec": {
            "name": "scroll_page",
            "description": "Scroll the page up or down by a number of pixels.",
            "inputSchema": {
                "json": {
                    "type": "object",
                    "properties": {
                        "direction": {"type": "string", "enum": ["up", "down"], "description": "Scroll direction."},
                        "pixels": {"type": "integer", "description": "Pixels to scroll. Default 500."},
                    },
                    "required": ["direction"],
                }
            },
        }
    },
    {
        "toolSpec": {
            "name": "wait",
            "description": "Wait for a given number of seconds before continuing.",
            "inputSchema": {
                "json": {
                    "type": "object",
                    "properties": {"seconds": {"type": "number", "description": "Seconds to wait."}},
                    "required": ["seconds"],
                }
            },
        }
    },
    {
        "toolSpec": {
            "name": "go_back",
            "description": "Navigate back to the previous page.",
            "inputSchema": {
                "json": {
                    "type": "object",
                    "properties": {},
                }
            },
        }
    },
    {
        "toolSpec": {
            "name": "extract_links",
            "description": "Extract all links (href + text) from the current page.",
            "inputSchema": {
                "json": {
                    "type": "object",
                    "properties": {},
                }
            },
        }
    },
]


class BedrockAgent:
    """Agentic loop using Bedrock Converse with tool use."""

    def __init__(self, config: BrowserOrchestratorConfig | None = None):
        self.config = config or BrowserOrchestratorConfig()
        self._client = boto3.client(
            "bedrock-runtime",
            region_name=self.config.aws_region,
        )

    def run(
        self,
        system_prompt: str,
        user_message: str,
        tool_executor: Any,
    ) -> str:
        """Run the agentic tool-use loop.

        Args:
            system_prompt: System-level instructions for the agent.
            user_message: The user query to fulfill.
            tool_executor: Callable(tool_name, tool_input) -> str that
                           executes browser tools and returns results.

        Returns:
            The agent's final text answer.
        """
        messages: list[dict] = [
            {"role": "user", "content": [{"text": user_message}]},
        ]

        for iteration in range(self.config.max_iterations):
            logger.info("Bedrock iteration %d/%d", iteration + 1, self.config.max_iterations)

            response = self._client.converse(
                modelId=self.config.bedrock_model_id,
                system=[{"text": system_prompt}],
                messages=messages,
                toolConfig={"tools": BROWSER_TOOLS},
                inferenceConfig={
                    "maxTokens": self.config.bedrock_max_tokens,
                    "temperature": self.config.bedrock_temperature,
                },
            )

            stop_reason = response["stopReason"]
            output_message = response["output"]["message"]
            messages.append(output_message)

            # If the model finished without calling tools → we're done
            if stop_reason == "end_turn":
                return self._extract_text(output_message)

            # If the model wants to use tools → execute them
            if stop_reason == "tool_use":
                tool_results = self._process_tool_calls(output_message, tool_executor)
                messages.append({
                    "role": "user",
                    "content": tool_results,
                })
                continue

            # Unexpected stop reason
            logger.warning("Unexpected stop_reason: %s", stop_reason)
            return self._extract_text(output_message)

        logger.warning("Max iterations reached (%d)", self.config.max_iterations)
        return self._extract_text(messages[-1]) if messages else "Max iterations reached."

    # ── Helpers ───────────────────────────────────────────────────────────────

    @staticmethod
    def _extract_text(message: dict) -> str:
        parts = []
        for block in message.get("content", []):
            if "text" in block:
                parts.append(block["text"])
        return "\n".join(parts) if parts else ""

    @staticmethod
    def _process_tool_calls(message: dict, tool_executor) -> list[dict]:
        results: list[dict] = []
        for block in message.get("content", []):
            if "toolUse" not in block:
                continue
            tool_use = block["toolUse"]
            tool_name = tool_use["name"]
            tool_input = tool_use.get("input", {})
            tool_use_id = tool_use["toolUseId"]

            logger.info("Tool call: %s(%s)", tool_name, json.dumps(tool_input, ensure_ascii=False))

            try:
                result_text = tool_executor(tool_name, tool_input)
                results.append({
                    "toolResult": {
                        "toolUseId": tool_use_id,
                        "content": [{"text": result_text}],
                    }
                })
            except Exception as exc:
                logger.error("Tool %s failed: %s", tool_name, exc)
                results.append({
                    "toolResult": {
                        "toolUseId": tool_use_id,
                        "content": [{"text": f"ERROR: {exc}"}],
                        "status": "error",
                    }
                })
        return results
