"""Demo: uso de las funciones MCP browser y gestión."""
from src.mcp_client import MCPClient
from src.browser import browser_navigate, browser_snapshot
from src.mcp_management import mcp_find


def main():
    with MCPClient() as client:
        # Listar herramientas disponibles
        tools = client.list_tools()
        print(f"Herramientas MCP disponibles: {len(tools)}")
        for tool in tools:
            print(f"  - {tool.get('name')}")

        # Ejemplo: navegar a una página
        result = browser_navigate("https://example.com", client=client)
        print(f"\nNavegación: {result}")

        # Ejemplo: tomar snapshot de accesibilidad
        snapshot = browser_snapshot(client=client)
        print(f"\nSnapshot: {snapshot}")

        # Ejemplo: buscar servidores MCP
        servers = mcp_find("browser", client=client)
        print(f"\nServidores MCP encontrados: {servers}")


if __name__ == "__main__":
    main()
