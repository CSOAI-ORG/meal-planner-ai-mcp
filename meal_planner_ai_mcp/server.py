from mcp.server.fastmcp import FastMCP

mcp = FastMCP("meal-planner")

SAMPLE_MEALS = {
    "breakfast": ["Oatmeal with berries", "Scrambled eggs and toast", "Greek yogurt with granola"],
    "lunch": ["Grilled chicken salad", "Quinoa bowl with veggies", "Turkey sandwich"],
    "dinner": ["Salmon with broccoli", "Stir-fry tofu and rice", "Pasta with marinara and meatballs"],
    "snack": ["Apple with almond butter", "Protein shake", "Hummus and carrots"],
}

FOOD_MACROS = {
    "chicken breast 100g": {"protein": 31, "carbs": 0, "fat": 3.6, "calories": 165},
    "rice 100g": {"protein": 2.7, "carbs": 28, "fat": 0.3, "calories": 130},
    "broccoli 100g": {"protein": 2.8, "carbs": 7, "fat": 0.4, "calories": 34},
    "egg 1": {"protein": 6, "carbs": 0.6, "fat": 5, "calories": 70},
    "oats 100g": {"protein": 13, "carbs": 68, "fat": 6.5, "calories": 389},
}

SUBSTITUTES = {
    "dairy": ["oat milk", "almond milk", "coconut yogurt"],
    "gluten": ["rice", "quinoa", "gluten-free bread"],
    "meat": ["tofu", "tempeh", "lentils"],
    "sugar": ["stevia", "monk fruit", "honey"],
}

@mcp.tool()
def plan_weekly_meals(diet: str = "balanced") -> dict:
    """Generate a weekly meal plan."""
    import random
    plan = {}
    for day in ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]:
        plan[day] = {
            "breakfast": random.choice(SAMPLE_MEALS["breakfast"]),
            "lunch": random.choice(SAMPLE_MEALS["lunch"]),
            "dinner": random.choice(SAMPLE_MEALS["dinner"]),
            "snack": random.choice(SAMPLE_MEALS["snack"]),
        }
    return {"diet": diet, "weekly_plan": plan}

@mcp.tool()
def calculate_daily_macros(foods: list) -> dict:
    """Sum macros from a list of food strings."""
    totals = {"protein": 0, "carbs": 0, "fat": 0, "calories": 0}
    recognized = []
    for food in foods:
        macros = FOOD_MACROS.get(food.lower())
        if macros:
            recognized.append(food)
            for k in totals:
                totals[k] += macros[k]
    return {"foods": recognized, "totals": {k: round(v, 1) for k, v in totals.items()}}

@mcp.tool()
def suggest_substitute(ingredient: str, restriction: str) -> dict:
    """Suggest a substitute."""
    options = SUBSTITUTES.get(restriction.lower())
    if not options:
        return {"error": "Restriction not found", "available": list(SUBSTITUTES.keys())}
    return {"ingredient": ingredient, "restriction": restriction, "substitutes": options}

def main():
    mcp.run(transport="stdio")

if __name__ == "__main__":
    main()
