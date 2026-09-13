"""
cap_09 — Servidor MCP mínimo: histórico de compras
Módulo 10, Seção 6: Model Context Protocol (MCP)

Expõe get_user_purchase_history como ferramenta MCP via stdio (modo padrão
para clientes locais como Claude Desktop ou o MCP Inspector). Em produção,
troque _FAKE_DB por uma query no seu Postgres/data warehouse.

Rodar: python cap_09/projeto/mcp_server_purchases.py
Inspecionar: npx @modelcontextprotocol/inspector python cap_09/projeto/mcp_server_purchases.py
"""
import asyncio

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

app = Server("purchases-mcp-server")

_FAKE_DB = {
    "alice@example.com": [
        {"sku": "BOOK-AGENTES-IA", "qty": 1, "date": "2026-04-12"},
        {"sku": "COURSE-LANGGRAPH", "qty": 1, "date": "2026-05-01"},
    ],
    "bob@example.com": [],
}


@app.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="get_user_purchase_history",
            description="Retorna o histórico de compras de um usuário dado seu e-mail.",
            inputSchema={
                "type": "object",
                "properties": {"email": {"type": "string", "format": "email"}},
                "required": ["email"],
            },
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    if name != "get_user_purchase_history":
        raise ValueError(f"Unknown tool: {name}")
    purchases = _FAKE_DB.get(arguments["email"], [])
    return [TextContent(type="text", text=str(purchases))]


async def main():
    async with stdio_server() as (read, write):
        await app.run(read, write, app.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
