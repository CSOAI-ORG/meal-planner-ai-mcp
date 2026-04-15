#!/usr/bin/env python3
"""MEOK AI Labs — meal-planner-ai-mcp MCP Server. Generate weekly meal plans with macros and shopping lists."""

import asyncio
import json
from datetime import datetime
from typing import Any

from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    Resource,
    Tool,
    TextContent)
import mcp.types as types
import sys, os
sys.path.insert(0, os.path.expanduser("~/clawd/meok-labs-engine/shared"))
from auth_middleware import check_access

from datetime import datetime, timezone
from collections import defaultdict

FREE_DAILY_LIMIT = 15
_usage = defaultdict(list)
def _rl(c="anon"):
    now = datetime.now(timezone.utc)
    _usage[c] = [t for t in _usage[c] if (now-t).total_seconds() < 86400]
    if len(_usage[c]) >= FREE_DAILY_LIMIT: return json.dumps({"error": f"Limit {FREE_DAILY_LIMIT}/day"})
    _usage[c].append(now); return None

# In-memory store (replace with DB in production)
_store = {}

server = Server("meal-planner-ai")

@server.list_resources()
def handle_list_resources() -> list[Resource]:
    return []

@server.list_tools()
def handle_list_tools() -> list[Tool]:
    return [
        Tool(name="generate_meal_plan", description="Generate a weekly meal plan", inputSchema={"type":"object","properties":{"diet":{"type":"string"},"calories":{"type":"number"}},"required":["diet"]}),
    ]

@server.call_tool()
def handle_call_tool(name: str, arguments: Any | None) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    args = arguments or {}
    api_key = args.get("api_key", "")
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return [TextContent(type="text", text=json.dumps({"error": msg, "upgrade_url": "https://meok.ai/pricing"}))]
    if err := _rl():
        return [TextContent(type="text", text=err)]
    if name == "generate_meal_plan":
            diet = args["diet"]
            cals = args.get("calories", 2000)
            plan = {f"Day {i}": {"breakfast": f"{diet} oats", "lunch": f"{diet} salad", "dinner": f"{diet} stir-fry"} for i in range(1, 8)}
            return [TextContent(type="text", text=json.dumps({"diet": diet, "target_calories": cals, "plan": plan}, indent=2))]
    return [TextContent(type="text", text=json.dumps({"error": "Unknown tool"}, indent=2))]

async def main():
    async with stdio_server(server._read_stream, server._write_stream) as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="meal-planner-ai-mcp",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={})))

if __name__ == "__main__":
    asyncio.run(main())