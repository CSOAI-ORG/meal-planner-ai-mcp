#!/usr/bin/env python3
"""MEOK AI Labs — meal-planner-ai-mcp MCP Server. Generate weekly meal plans with macros and shopping lists."""

import json
from datetime import datetime, timezone
from collections import defaultdict

from mcp.server.fastmcp import FastMCP
import sys, os
sys.path.insert(0, os.path.expanduser("~/clawd/meok-labs-engine/shared"))
from auth_middleware import check_access

FREE_DAILY_LIMIT = 15
_usage = defaultdict(list)
def _rl(c="anon"):
    now = datetime.now(timezone.utc)
    _usage[c] = [t for t in _usage[c] if (now-t).total_seconds() < 86400]
    if len(_usage[c]) >= FREE_DAILY_LIMIT: return json.dumps({"error": f"Limit {FREE_DAILY_LIMIT}/day"})
    _usage[c].append(now); return None

MEAL_DB = {
    "standard": {
        "breakfast": [
            {"name": "Oatmeal with berries", "cal": 350, "protein": 12, "carbs": 55, "fat": 8, "ingredients": ["oats", "mixed berries", "milk", "honey"]},
            {"name": "Scrambled eggs on toast", "cal": 400, "protein": 22, "carbs": 30, "fat": 20, "ingredients": ["eggs", "bread", "butter", "salt"]},
            {"name": "Greek yogurt parfait", "cal": 300, "protein": 18, "carbs": 40, "fat": 8, "ingredients": ["greek yogurt", "granola", "honey", "berries"]},
            {"name": "Avocado toast", "cal": 380, "protein": 10, "carbs": 35, "fat": 22, "ingredients": ["bread", "avocado", "lemon", "salt", "chili flakes"]},
        ],
        "lunch": [
            {"name": "Grilled chicken salad", "cal": 450, "protein": 35, "carbs": 20, "fat": 25, "ingredients": ["chicken breast", "mixed greens", "tomato", "cucumber", "olive oil"]},
            {"name": "Turkey wrap", "cal": 420, "protein": 28, "carbs": 40, "fat": 16, "ingredients": ["tortilla", "turkey", "lettuce", "tomato", "mayo"]},
            {"name": "Quinoa bowl", "cal": 480, "protein": 18, "carbs": 60, "fat": 18, "ingredients": ["quinoa", "chickpeas", "cucumber", "feta", "olive oil"]},
            {"name": "Tuna sandwich", "cal": 400, "protein": 30, "carbs": 35, "fat": 14, "ingredients": ["bread", "tuna", "mayo", "lettuce", "tomato"]},
        ],
        "dinner": [
            {"name": "Salmon with vegetables", "cal": 520, "protein": 38, "carbs": 25, "fat": 28, "ingredients": ["salmon fillet", "broccoli", "rice", "lemon", "olive oil"]},
            {"name": "Chicken stir-fry", "cal": 480, "protein": 32, "carbs": 45, "fat": 18, "ingredients": ["chicken breast", "bell peppers", "soy sauce", "rice", "ginger"]},
            {"name": "Pasta with meat sauce", "cal": 550, "protein": 28, "carbs": 65, "fat": 18, "ingredients": ["pasta", "ground beef", "tomato sauce", "onion", "garlic"]},
            {"name": "Grilled fish tacos", "cal": 460, "protein": 30, "carbs": 40, "fat": 20, "ingredients": ["white fish", "tortillas", "cabbage", "lime", "avocado"]},
        ],
    },
    "vegetarian": {
        "breakfast": [
            {"name": "Smoothie bowl", "cal": 380, "protein": 14, "carbs": 55, "fat": 12, "ingredients": ["banana", "spinach", "protein powder", "berries", "granola"]},
            {"name": "Veggie omelette", "cal": 350, "protein": 20, "carbs": 10, "fat": 25, "ingredients": ["eggs", "spinach", "mushrooms", "cheese", "tomato"]},
        ],
        "lunch": [
            {"name": "Lentil soup", "cal": 400, "protein": 22, "carbs": 55, "fat": 8, "ingredients": ["lentils", "carrots", "celery", "onion", "cumin"]},
            {"name": "Caprese sandwich", "cal": 420, "protein": 18, "carbs": 40, "fat": 22, "ingredients": ["bread", "mozzarella", "tomato", "basil", "olive oil"]},
        ],
        "dinner": [
            {"name": "Vegetable curry", "cal": 450, "protein": 15, "carbs": 55, "fat": 20, "ingredients": ["chickpeas", "coconut milk", "spinach", "rice", "curry paste"]},
            {"name": "Stuffed bell peppers", "cal": 400, "protein": 18, "carbs": 45, "fat": 16, "ingredients": ["bell peppers", "rice", "black beans", "corn", "cheese"]},
        ],
    },
    "keto": {
        "breakfast": [
            {"name": "Bacon and eggs", "cal": 450, "protein": 28, "carbs": 2, "fat": 36, "ingredients": ["bacon", "eggs", "butter"]},
            {"name": "Keto smoothie", "cal": 350, "protein": 20, "carbs": 5, "fat": 28, "ingredients": ["almond milk", "protein powder", "almond butter", "cocoa"]},
        ],
        "lunch": [
            {"name": "Cobb salad", "cal": 500, "protein": 35, "carbs": 8, "fat": 38, "ingredients": ["chicken", "bacon", "egg", "avocado", "blue cheese"]},
            {"name": "Lettuce wrap burgers", "cal": 480, "protein": 32, "carbs": 5, "fat": 36, "ingredients": ["ground beef", "lettuce", "cheese", "tomato", "mustard"]},
        ],
        "dinner": [
            {"name": "Grilled steak with asparagus", "cal": 550, "protein": 42, "carbs": 6, "fat": 40, "ingredients": ["steak", "asparagus", "butter", "garlic"]},
            {"name": "Baked salmon with spinach", "cal": 500, "protein": 38, "carbs": 4, "fat": 36, "ingredients": ["salmon", "spinach", "olive oil", "lemon", "garlic"]},
        ],
    },
}

SUBSTITUTION_MAP = {
    "chicken": ["tofu", "tempeh", "seitan"],
    "beef": ["lentils", "mushrooms", "jackfruit"],
    "salmon": ["tofu steaks", "portobello mushroom"],
    "eggs": ["tofu scramble", "chickpea flour omelette"],
    "milk": ["oat milk", "almond milk", "soy milk"],
    "cheese": ["nutritional yeast", "cashew cheese", "vegan cheese"],
    "butter": ["olive oil", "coconut oil", "avocado"],
    "bread": ["lettuce wraps", "rice cakes", "gluten-free bread"],
    "pasta": ["zucchini noodles", "rice noodles", "spaghetti squash"],
    "rice": ["cauliflower rice", "quinoa", "bulgur"],
}

DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

mcp = FastMCP("meal-planner-ai", instructions="Plan meals, calculate nutrition, generate shopping lists, and suggest substitutes.")


@mcp.tool()
def plan_meals(diet: str = "standard", calories: int = 2000, days: int = 7, api_key: str = "") -> str:
    """Generate a meal plan for the specified diet type and calorie target."""
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return json.dumps({"error": msg, "upgrade_url": "https://meok.ai/pricing"})
    if err := _rl(): return err

    diet_key = diet.lower() if diet.lower() in MEAL_DB else "standard"
    meals = MEAL_DB[diet_key]
    plan = {}
    total_cals = 0

    for i in range(min(days, 7)):
        day = DAYS[i]
        b = meals["breakfast"][i % len(meals["breakfast"])]
        l = meals["lunch"][i % len(meals["lunch"])]
        d = meals["dinner"][i % len(meals["dinner"])]
        day_cals = b["cal"] + l["cal"] + d["cal"]
        total_cals += day_cals
        plan[day] = {
            "breakfast": {"meal": b["name"], "calories": b["cal"]},
            "lunch": {"meal": l["name"], "calories": l["cal"]},
            "dinner": {"meal": d["name"], "calories": d["cal"]},
            "total_calories": day_cals,
        }

    avg_daily = round(total_cals / min(days, 7))
    diff = avg_daily - calories

    return json.dumps({
        "diet": diet_key,
        "target_calories": calories,
        "average_daily_calories": avg_daily,
        "calorie_difference": diff,
        "adjustment_note": f"{'Reduce' if diff > 0 else 'Increase'} portions by ~{abs(round(diff/avg_daily*100))}% to hit target" if abs(diff) > 100 else "On target",
        "days": min(days, 7),
        "plan": plan,
    }, indent=2)


@mcp.tool()
def calculate_macros(meals: list[str], diet: str = "standard", api_key: str = "") -> str:
    """Calculate macronutrient totals for a list of meal names."""
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return json.dumps({"error": msg, "upgrade_url": "https://meok.ai/pricing"})
    if err := _rl(): return err

    diet_key = diet.lower() if diet.lower() in MEAL_DB else "standard"
    all_meals = []
    for meal_type in MEAL_DB[diet_key].values():
        all_meals.extend(meal_type)

    totals = {"calories": 0, "protein": 0, "carbs": 0, "fat": 0}
    matched = []
    unmatched = []

    for meal_name in meals:
        found = False
        for m in all_meals:
            if meal_name.lower() in m["name"].lower() or m["name"].lower() in meal_name.lower():
                totals["calories"] += m["cal"]
                totals["protein"] += m["protein"]
                totals["carbs"] += m["carbs"]
                totals["fat"] += m["fat"]
                matched.append({"name": m["name"], "cal": m["cal"], "protein": m["protein"], "carbs": m["carbs"], "fat": m["fat"]})
                found = True
                break
        if not found:
            unmatched.append(meal_name)

    # Macro percentages
    total_macro_cals = totals["protein"] * 4 + totals["carbs"] * 4 + totals["fat"] * 9
    if total_macro_cals > 0:
        macro_split = {
            "protein": f"{round(totals['protein'] * 4 / total_macro_cals * 100)}%",
            "carbs": f"{round(totals['carbs'] * 4 / total_macro_cals * 100)}%",
            "fat": f"{round(totals['fat'] * 9 / total_macro_cals * 100)}%",
        }
    else:
        macro_split = {"protein": "0%", "carbs": "0%", "fat": "0%"}

    return json.dumps({
        "matched_meals": matched,
        "unmatched": unmatched,
        "totals": totals,
        "macro_split": macro_split,
    }, indent=2)


@mcp.tool()
def generate_shopping_list(diet: str = "standard", days: int = 7, api_key: str = "") -> str:
    """Generate a consolidated shopping list for a meal plan."""
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return json.dumps({"error": msg, "upgrade_url": "https://meok.ai/pricing"})
    if err := _rl(): return err

    diet_key = diet.lower() if diet.lower() in MEAL_DB else "standard"
    meals_data = MEAL_DB[diet_key]
    ingredient_counts = defaultdict(int)

    for i in range(min(days, 7)):
        for meal_type in meals_data.values():
            meal = meal_type[i % len(meal_type)]
            for ing in meal["ingredients"]:
                ingredient_counts[ing] += 1

    # Categorize ingredients
    categories = {
        "produce": ["berries", "mixed berries", "banana", "spinach", "tomato", "cucumber", "lettuce",
                     "broccoli", "bell peppers", "asparagus", "mushrooms", "onion", "garlic", "ginger",
                     "avocado", "cabbage", "lime", "lemon", "mixed greens", "basil", "carrots", "celery", "corn"],
        "protein": ["chicken breast", "turkey", "salmon fillet", "ground beef", "white fish", "tuna",
                     "eggs", "bacon", "steak", "chicken", "tofu", "lentils", "chickpeas", "black beans"],
        "dairy": ["milk", "greek yogurt", "cheese", "butter", "mozzarella", "feta", "blue cheese",
                   "cream cheese", "almond milk", "coconut milk", "soy milk", "oat milk"],
        "pantry": ["oats", "bread", "tortilla", "quinoa", "rice", "pasta", "granola", "honey",
                    "olive oil", "soy sauce", "tomato sauce", "curry paste", "mustard", "mayo",
                    "salt", "chili flakes", "cumin", "protein powder", "cocoa", "almond butter",
                    "nutritional yeast"],
    }

    categorized = defaultdict(list)
    uncategorized = []
    for ing, count in sorted(ingredient_counts.items()):
        placed = False
        for cat, items in categories.items():
            if ing in items:
                categorized[cat].append({"item": ing, "times_needed": count})
                placed = True
                break
        if not placed:
            uncategorized.append({"item": ing, "times_needed": count})

    return json.dumps({
        "diet": diet_key,
        "days": min(days, 7),
        "total_items": len(ingredient_counts),
        "shopping_list": dict(categorized),
        "other": uncategorized,
    }, indent=2)


@mcp.tool()
def suggest_substitutes(ingredient: str, reason: str = "preference", api_key: str = "") -> str:
    """Suggest ingredient substitutes for dietary restrictions, allergies, or preferences."""
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return json.dumps({"error": msg, "upgrade_url": "https://meok.ai/pricing"})
    if err := _rl(): return err

    lower = ingredient.lower()
    substitutes = []

    # Direct match
    if lower in SUBSTITUTION_MAP:
        substitutes = SUBSTITUTION_MAP[lower]
    else:
        # Partial match
        for key, subs in SUBSTITUTION_MAP.items():
            if key in lower or lower in key:
                substitutes = subs
                break

    if not substitutes:
        substitutes = ["Check specialty stores for alternatives"]

    notes = {
        "allergy": "Ensure substitutes are free from your specific allergen",
        "vegan": "All suggested options are plant-based",
        "preference": "Substitutes have similar texture and cooking properties",
        "availability": "These alternatives are commonly available in most supermarkets",
    }

    return json.dumps({
        "original": ingredient,
        "reason": reason,
        "substitutes": substitutes,
        "note": notes.get(reason, "Choose based on your dietary needs"),
        "tip": f"When substituting {ingredient}, adjust cooking times as needed",
    }, indent=2)


if __name__ == "__main__":
    mcp.run()
