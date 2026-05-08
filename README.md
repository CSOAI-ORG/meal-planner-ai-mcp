<div align="center">

# Meal Planner Ai MCP

**MCP server for meal planner ai mcp operations**

[![PyPI](https://img.shields.io/pypi/v/meok-meal-planner-ai-mcp)](https://pypi.org/project/meok-meal-planner-ai-mcp/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![MEOK AI Labs](https://img.shields.io/badge/MEOK_AI_Labs-MCP_Server-purple)](https://meok.ai)

</div>

## Overview

Meal Planner Ai MCP provides AI-powered tools via the Model Context Protocol (MCP).

## Tools

| Tool | Description |
|------|-------------|
| `plan_meals` | Generate a meal plan for the specified diet type and calorie target. |
| `calculate_macros` | Calculate macronutrient totals for a list of meal names. |
| `generate_shopping_list` | Generate a consolidated shopping list for a meal plan. |
| `suggest_substitutes` | Suggest ingredient substitutes for dietary restrictions, allergies, or preferenc |

## Installation

```bash
pip install meok-meal-planner-ai-mcp
```

## Usage with Claude Desktop

Add to your Claude Desktop MCP config (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "meal-planner-ai": {
      "command": "python",
      "args": ["-m", "meok_meal_planner_ai_mcp.server"]
    }
  }
}
```

## Usage with FastMCP

```python
from mcp.server.fastmcp import FastMCP

# This server exposes 4 tool(s) via MCP
# See server.py for full implementation
```

## License

MIT © [MEOK AI Labs](https://meok.ai)
