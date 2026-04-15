# Meal Planner AI

> By [MEOK AI Labs](https://meok.ai) — Plan meals, calculate nutrition, generate shopping lists, and suggest substitutes

## Installation

```bash
pip install meal-planner-ai-mcp
```

## Usage

```bash
python server.py
```

## Tools

### `plan_meals`
Generate a meal plan for the specified diet type and calorie target.

**Parameters:**
- `diet` (str): Diet type: standard, vegetarian, keto (default: "standard")
- `calories` (int): Daily calorie target (default: 2000)
- `days` (int): Number of days to plan (default: 7)

### `calculate_macros`
Calculate macronutrient totals for a list of meal names.

**Parameters:**
- `meals` (list[str]): List of meal names
- `diet` (str): Diet type for database lookup (default: "standard")

### `generate_shopping_list`
Generate a consolidated, categorized shopping list for a meal plan.

**Parameters:**
- `diet` (str): Diet type (default: "standard")
- `days` (int): Number of days (default: 7)

### `suggest_substitutes`
Suggest ingredient substitutes for dietary restrictions, allergies, or preferences.

**Parameters:**
- `ingredient` (str): Ingredient to substitute
- `reason` (str): Reason: allergy, vegan, preference, availability (default: "preference")

## Authentication

Free tier: 15 calls/day. Upgrade at [meok.ai/pricing](https://meok.ai/pricing) for unlimited access.

## License

MIT — MEOK AI Labs
