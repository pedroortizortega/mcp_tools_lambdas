"""Configuration for the browser orchestrator."""
from __future__ import annotations

import os
from dataclasses import dataclass, field


@dataclass
class BrowserOrchestratorConfig:
    """All settings for the browser agent orchestrator."""

    # AWS Bedrock
    aws_region: str = field(default_factory=lambda: os.getenv("AWS_REGION", "us-east-1"))
    bedrock_model_id: str = field(
        default_factory=lambda: os.getenv(
            "BEDROCK_MODEL_ID",
            "anthropic.claude-sonnet-4-20250514-v1:0",
        )
    )
    bedrock_max_tokens: int = int(os.getenv("BEDROCK_MAX_TOKENS", "4096"))
    bedrock_temperature: float = float(os.getenv("BEDROCK_TEMPERATURE", "0.3"))

    # Agent loop
    max_iterations: int = int(os.getenv("AGENT_MAX_ITERATIONS", "15"))

    # Playwright
    headless: bool = os.getenv("BROWSER_HEADLESS", "true").lower() == "true"
    viewport_width: int = int(os.getenv("BROWSER_VIEWPORT_WIDTH", "1280"))
    viewport_height: int = int(os.getenv("BROWSER_VIEWPORT_HEIGHT", "720"))

    # FastAPI
    host: str = os.getenv("HOST", "0.0.0.0")
    port: int = int(os.getenv("PORT", "8000"))
