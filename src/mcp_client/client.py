import uuid
import httpx
from .config import MCPConfig


class MCPError(Exception):
    def __init__(self, code: int, message: str, data: dict | None = None):
        self.code = code
        self.message = message
        self.data = data
        super().__init__(f"MCP Error {code}: {message}")


class MCPClient:
    def __init__(self, config: MCPConfig | None = None):
        self.config = config or MCPConfig()
        self._http = httpx.Client(timeout=self.config.timeout)

    def call_tool(self, tool_name: str, arguments: dict | None = None) -> dict:
        """Send a JSON-RPC 2.0 tools/call request to the MCP gateway."""
        payload = {
            "jsonrpc": "2.0",
            "id": str(uuid.uuid4()),
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments or {},
            },
        }
        response = self._http.post(
            self.config.tools_url,
            json=payload,
            headers={"Content-Type": "application/json"},
        )
        response.raise_for_status()
        body = response.json()

        if "error" in body:
            err = body["error"]
            raise MCPError(err.get("code", -1), err.get("message", "Unknown error"), err.get("data"))

        return body.get("result", {})

    def list_tools(self) -> list[dict]:
        """List all tools available on the MCP gateway."""
        payload = {
            "jsonrpc": "2.0",
            "id": str(uuid.uuid4()),
            "method": "tools/list",
            "params": {},
        }
        response = self._http.post(
            self.config.tools_url,
            json=payload,
            headers={"Content-Type": "application/json"},
        )
        response.raise_for_status()
        body = response.json()
        return body.get("result", {}).get("tools", [])

    def close(self):
        self._http.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()
