import os
from dataclasses import dataclass


@dataclass
class MCPConfig:
    endpoint: str = os.getenv("MCP_GATEWAY_URL", "http://localhost:8811")
    timeout: float = float(os.getenv("MCP_TIMEOUT", "30.0"))

    @property
    def tools_url(self) -> str:
        return f"{self.endpoint}/mcp"
