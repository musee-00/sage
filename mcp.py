#!/usr/bin/env python3
"""MCP-server som exponerar Claude-agenten till VS Code."""

import asyncio
import json
import sys
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp import types

import agent as agent_module

app = Server("claude-kodassistent")


@app.list_tools()
async def list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="ask_agent",
            description=(
                "Skicka en fråga eller uppgift till Claude-kodassistenten. "
                "Agenten kan läsa filer, köra kommandon och söka i kod."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Din fråga eller uppgift till agenten.",
                    },
                    "system_prompt": {
                        "type": "string",
                        "description": "Valfri systemprompt för att anpassa agentens beteende.",
                    },
                },
                "required": ["query"],
            },
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[types.TextContent]:
    if name != "ask_agent":
        raise ValueError(f"Okänt verktyg: {name}")

    query: str = arguments["query"]
    system_prompt: str | None = arguments.get("system_prompt")

    # Kör agenten i en tråd så vi inte blockerar event loop
    loop = asyncio.get_event_loop()
    response, _ = await loop.run_in_executor(
        None,
        lambda: agent_module.run_agent(query, system_prompt=system_prompt),
    )

    return [types.TextContent(type="text", text=response)]


async def main() -> None:
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
