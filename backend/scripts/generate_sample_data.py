"""Generate a small, self-contained sample dataset.

The full Food.com dataset (RAW_recipes.csv / RAW_interactions.csv) is ~900 MB
and takes minutes to import, which is too heavy for a "docker compose up" demo.

This script builds a compact, deterministic sample that keeps the exact column
layout of the real dataset, so the application is fully usable out of the box
and the same code path also works when the full data is loaded later.

Output:
    data/recipes_sample.csv
    data/interactions_sample.csv

Run:
    python backend/scripts/generate_sample_data.py
"""

import csv
import os
import random
from datetime import date, timedelta

# Deterministic output so the committed CSVs never change unexpectedly.
random.seed(42)

HERE = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.normpath(os.path.join(HERE, "..", "..", "data"))

# A curated pool of common recipes described in the style of Food.com.
# Each entry: (name, minutes, cuisine, ingredients, extra_tags, description)
RECIPES = [
    ("classic margherita pizza", 45, "italian",
     ["flour", "tomato", "mozzarella", "basil", "olive oil", "yeast", "salt"],
     ["vegetarian", "dinner", "baking"],
     "A simple Neapolitan-style pizza with fresh basil and mozzarella."),
    ("spaghetti aglio e olio", 20, "italian",
     ["spaghetti", "garlic", "olive oil", "chili flakes", "parsley", "salt"],
     ["vegetarian", "quick", "dinner", "pasta"],
     "Garlic and oil pasta that comes together in minutes."),
    ("creamy mushroom risotto", 40, "italian",
     ["arborio rice", "mushroom", "onion", "parmesan", "butter", "white wine", "stock"],
     ["vegetarian", "dinner", "comfort-food"],
     "Slow-stirred risotto with earthy mushrooms."),
    ("chicken tikka masala", 55, "indian",
     ["chicken", "yogurt", "tomato", "onion", "garlic", "ginger", "garam masala", "cream"],
     ["dinner", "spicy", "curry"],
     "Grilled chicken in a spiced creamy tomato sauce."),
    ("chana masala", 35, "indian",
     ["chickpeas", "tomato", "onion", "garlic", "ginger", "cumin", "coriander", "chili"],
     ["vegetarian", "vegan", "curry", "dinner"],
     "A tangy chickpea curry with warming spices."),
    ("vegetable biryani", 60, "indian",
     ["basmati rice", "carrot", "peas", "onion", "yogurt", "garam masala", "saffron", "mint"],
     ["vegetarian", "dinner", "rice"],
     "Fragrant layered rice with mixed vegetables."),
    ("beef tacos", 30, "mexican",
     ["beef", "tortilla", "onion", "tomato", "cheese", "cumin", "chili", "lettuce"],
     ["dinner", "quick", "spicy"],
     "Weeknight ground beef tacos with fresh toppings."),
    ("black bean quesadilla", 20, "mexican",
     ["black beans", "tortilla", "cheese", "onion", "bell pepper", "cumin"],
     ["vegetarian", "quick", "lunch"],
     "Crispy quesadillas stuffed with beans and cheese."),
    ("guacamole", 15, "mexican",
     ["avocado", "lime", "onion", "tomato", "cilantro", "salt"],
     ["vegetarian", "vegan", "snack", "quick", "no-cook"],
     "Fresh chunky guacamole for dipping."),
    ("chicken fried rice", 25, "chinese",
     ["rice", "chicken", "egg", "soy sauce", "peas", "carrot", "garlic", "green onion"],
     ["dinner", "quick"],
     "A fast stir-fried rice using leftover rice."),
    ("kung pao tofu", 30, "chinese",
     ["tofu", "peanuts", "bell pepper", "soy sauce", "garlic", "chili", "ginger"],
     ["vegetarian", "vegan", "spicy", "dinner"],
     "Sticky, spicy tofu with crunchy peanuts."),
    ("egg drop soup", 15, "chinese",
     ["egg", "stock", "corn starch", "green onion", "soy sauce", "ginger"],
     ["quick", "soup", "lunch"],
     "A silky soup that is ready in minutes."),
    ("miso ramen", 40, "japanese",
     ["ramen noodles", "miso", "stock", "egg", "green onion", "garlic", "ginger", "corn"],
     ["dinner", "soup", "comfort-food"],
     "A warming bowl of miso ramen with a soft egg."),
    ("teriyaki salmon", 25, "japanese",
     ["salmon", "soy sauce", "honey", "garlic", "ginger", "rice", "sesame"],
     ["dinner", "quick", "seafood"],
     "Pan-seared salmon glazed in teriyaki."),
    ("vegetable tempura", 35, "japanese",
     ["flour", "carrot", "sweet potato", "zucchini", "soda water", "oil", "salt"],
     ["vegetarian", "fried"],
     "Light, crispy battered vegetables."),
    ("greek salad", 15, "greek",
     ["cucumber", "tomato", "feta", "olives", "onion", "olive oil", "oregano"],
     ["vegetarian", "salad", "no-cook", "quick", "healthy"],
     "A crisp, refreshing no-cook salad."),
    ("hummus", 10, "middle-eastern",
     ["chickpeas", "tahini", "lemon", "garlic", "olive oil", "cumin"],
     ["vegetarian", "vegan", "snack", "quick"],
     "Smooth homemade hummus."),
    ("falafel wrap", 40, "middle-eastern",
     ["chickpeas", "onion", "garlic", "parsley", "cumin", "flour", "tortilla", "tahini"],
     ["vegetarian", "vegan", "lunch"],
     "Crispy falafel wrapped with tahini sauce."),
    ("french onion soup", 60, "french",
     ["onion", "butter", "stock", "bread", "cheese", "thyme", "white wine"],
     ["soup", "comfort-food", "dinner"],
     "Deeply caramelized onion soup with a cheesy crust."),
    ("ratatouille", 50, "french",
     ["eggplant", "zucchini", "tomato", "bell pepper", "onion", "garlic", "olive oil", "thyme"],
     ["vegetarian", "vegan", "healthy", "dinner"],
     "A rustic stew of summer vegetables."),
    ("banana pancakes", 20, "american",
     ["flour", "banana", "egg", "milk", "baking powder", "butter", "sugar"],
     ["breakfast", "vegetarian", "quick", "sweet"],
     "Fluffy pancakes sweetened with ripe banana."),
    ("classic beef burger", 25, "american",
     ["beef", "bun", "cheese", "lettuce", "tomato", "onion", "pickle"],
     ["dinner", "quick"],
     "A juicy homemade cheeseburger."),
    ("mac and cheese", 35, "american",
     ["macaroni", "cheese", "milk", "butter", "flour", "breadcrumbs"],
     ["vegetarian", "comfort-food", "dinner"],
     "Creamy baked macaroni and cheese."),
    ("caesar salad", 20, "american",
     ["romaine", "parmesan", "croutons", "garlic", "lemon", "olive oil", "egg"],
     ["salad", "lunch"],
     "Crisp romaine with a garlicky dressing."),
    ("tomato basil soup", 30, "american",
     ["tomato", "onion", "garlic", "basil", "cream", "stock", "butter"],
     ["vegetarian", "soup", "comfort-food"],
     "A smooth tomato soup with fresh basil."),
    ("thai green curry", 40, "thai",
     ["chicken", "coconut milk", "green curry paste", "bamboo", "basil", "fish sauce", "eggplant"],
     ["dinner", "spicy", "curry"],
     "A creamy coconut curry with fragrant basil."),
    ("pad thai", 30, "thai",
     ["rice noodles", "shrimp", "egg", "peanuts", "bean sprouts", "tamarind", "fish sauce", "lime"],
     ["dinner", "quick", "seafood"],
     "Sweet and tangy stir-fried noodles."),
    ("mango sticky rice", 45, "thai",
     ["glutinous rice", "mango", "coconut milk", "sugar", "salt"],
     ["dessert", "vegetarian", "vegan", "sweet"],
     "A classic Thai dessert with sweet coconut rice."),
    ("shakshuka", 30, "middle-eastern",
     ["egg", "tomato", "bell pepper", "onion", "garlic", "cumin", "paprika"],
     ["vegetarian", "breakfast", "brunch"],
     "Eggs poached in a spiced tomato sauce."),
    ("caprese sandwich", 10, "italian",
     ["bread", "mozzarella", "tomato", "basil", "olive oil", "balsamic"],
     ["vegetarian", "quick", "lunch", "no-cook"],
     "A simple fresh mozzarella and tomato sandwich."),
    ("lentil soup", 40, "middle-eastern",
     ["lentils", "onion", "carrot", "garlic", "cumin", "tomato", "stock"],
     ["vegetarian", "vegan", "soup", "healthy"],
     "A hearty, protein-rich lentil soup."),
    ("stuffed bell peppers", 55, "american",
     ["bell pepper", "rice", "beef", "tomato", "onion", "cheese", "garlic"],
     ["dinner", "comfort-food"],
     "Peppers baked with a savory rice and beef filling."),
    ("veggie stir fry", 20, "chinese",
     ["broccoli", "carrot", "bell pepper", "soy sauce", "garlic", "ginger", "sesame"],
     ["vegetarian", "vegan", "quick", "healthy", "dinner"],
     "A colorful vegetable stir fry."),
    ("chocolate chip cookies", 30, "american",
     ["flour", "butter", "sugar", "egg", "chocolate chips", "vanilla", "baking soda"],
     ["dessert", "vegetarian", "baking", "sweet"],
     "Chewy cookies loaded with chocolate."),
    ("apple pie", 75, "american",
     ["flour", "butter", "apple", "sugar", "cinnamon", "lemon", "egg"],
     ["dessert", "vegetarian", "baking", "sweet"],
     "A flaky double-crust apple pie."),
    ("blueberry muffins", 35, "american",
     ["flour", "blueberry", "sugar", "egg", "milk", "butter", "baking powder"],
     ["breakfast", "vegetarian", "baking", "sweet"],
     "Soft muffins bursting with blueberries."),
    ("minestrone soup", 45, "italian",
     ["beans", "tomato", "carrot", "celery", "onion", "pasta", "zucchini", "stock"],
     ["vegetarian", "vegan", "soup", "healthy"],
     "A chunky Italian vegetable and bean soup."),
    ("chicken noodle soup", 40, "american",
     ["chicken", "noodles", "carrot", "celery", "onion", "garlic", "stock"],
     ["soup", "comfort-food", "dinner"],
     "Classic comforting chicken noodle soup."),
    ("shrimp scampi", 20, "italian",
     ["shrimp", "garlic", "butter", "white wine", "lemon", "parsley", "spaghetti"],
     ["dinner", "quick", "seafood"],
     "Garlicky shrimp tossed with pasta."),
    ("veggie omelette", 15, "american",
     ["egg", "bell pepper", "onion", "cheese", "spinach", "butter"],
     ["breakfast", "vegetarian", "quick"],
     "A fluffy omelette packed with vegetables."),
    ("sweet potato curry", 40, "indian",
     ["sweet potato", "coconut milk", "onion", "garlic", "ginger", "spinach", "curry powder"],
     ["vegetarian", "vegan", "curry", "healthy", "dinner"],
     "A creamy vegan curry with sweet potato and spinach."),
    ("beef stir fry", 25, "chinese",
     ["beef", "broccoli", "soy sauce", "garlic", "ginger", "corn starch", "green onion"],
     ["dinner", "quick"],
     "Tender beef and broccoli in a savory sauce."),
    ("caprese pasta salad", 20, "italian",
     ["pasta", "tomato", "mozzarella", "basil", "olive oil", "balsamic"],
     ["vegetarian", "salad", "lunch"],
     "A cold pasta salad with mozzarella and basil."),
    ("tuna salad sandwich", 10, "american",
     ["tuna", "mayonnaise", "celery", "onion", "bread", "lemon"],
     ["lunch", "quick", "no-cook"],
     "A quick tuna salad sandwich."),
    ("potato leek soup", 45, "french",
     ["potato", "leek", "onion", "butter", "cream", "stock"],
     ["vegetarian", "soup", "comfort-food"],
     "A silky pureed potato and leek soup."),
    ("baked ziti", 50, "italian",
     ["ziti", "tomato", "mozzarella", "ricotta", "garlic", "onion", "basil"],
     ["vegetarian", "dinner", "baking", "comfort-food"],
     "Cheesy baked pasta with tomato sauce."),
    ("chicken caesar wrap", 15, "american",
     ["chicken", "tortilla", "romaine", "parmesan", "caesar dressing"],
     ["lunch", "quick"],
     "A portable version of the caesar salad."),
    ("veggie burrito bowl", 25, "mexican",
     ["rice", "black beans", "corn", "avocado", "tomato", "lime", "cilantro"],
     ["vegetarian", "vegan", "healthy", "lunch"],
     "A build-your-own bowl with beans and rice."),
    ("pumpkin soup", 40, "american",
     ["pumpkin", "onion", "garlic", "cream", "stock", "nutmeg", "butter"],
     ["vegetarian", "soup", "healthy"],
     "A velvety spiced pumpkin soup."),
    ("garlic butter shrimp", 15, "american",
     ["shrimp", "garlic", "butter", "lemon", "parsley", "chili flakes"],
     ["quick", "seafood", "dinner"],
     "Juicy shrimp in a garlic butter sauce."),
]

RECIPE_HEADER = [
    "name", "id", "minutes", "contributor_id", "submitted", "tags",
    "nutrition", "n_steps", "steps", "description", "ingredients", "n_ingredients",
]

INTERACTION_HEADER = ["user_id", "recipe_id", "date", "rating", "review"]

POSITIVE_REVIEWS = [
    "Loved this, will make again!",
    "So easy and tasty.",
    "A new family favorite.",
    "Great flavors, highly recommend.",
    "Perfect for a weeknight.",
    "Delicious and simple.",
]
NEUTRAL_REVIEWS = [
    "It was okay, needed more seasoning.",
    "Decent but nothing special.",
    "Good base recipe to build on.",
]


def build_recipes():
    """Return a list of recipe rows shaped like RAW_recipes.csv."""
    rows = []
    start = date(2008, 1, 1)
    for index, (name, minutes, cuisine, ingredients, extra_tags, description) in enumerate(RECIPES):
        recipe_id = 100000 + index
        tags = [cuisine] + extra_tags
        # Rough, plausible nutrition list: [calories, fat, sugar, sodium, protein, sat_fat, carbs]
        calories = 120 + len(ingredients) * 35 + minutes
        nutrition = [
            float(calories),
            round(calories * 0.05, 1),
            round(calories * 0.08, 1),
            round(calories * 0.10, 1),
            round(len(ingredients) * 2.5, 1),
            round(calories * 0.02, 1),
            round(calories * 0.12, 1),
        ]
        steps = [
            "gather and prepare all ingredients",
            "cook following the classic method",
            "season to taste and serve",
        ]
        rows.append({
            "name": name,
            "id": recipe_id,
            "minutes": minutes,
            "contributor_id": 2000 + (index % 15),
            "submitted": (start + timedelta(days=index * 37)).isoformat(),
            "tags": str(tags),
            "nutrition": str(nutrition),
            "n_steps": len(steps),
            "steps": str(steps),
            "description": description,
            "ingredients": str(ingredients),
            "n_ingredients": len(ingredients),
        })
    return rows


def build_interactions(recipes):
    """Return synthetic user ratings so collaborative signals exist."""
    rows = []
    n_users = 40
    start = date(2015, 1, 1)
    for user_id in range(1, n_users + 1):
        # Each user rates a random handful of recipes.
        sampled = random.sample(recipes, random.randint(4, 9))
        for recipe in sampled:
            rating = random.choices([3, 4, 5], weights=[1, 3, 6])[0]
            review = random.choice(POSITIVE_REVIEWS if rating >= 4 else NEUTRAL_REVIEWS)
            rows.append({
                "user_id": user_id,
                "recipe_id": recipe["id"],
                "date": (start + timedelta(days=random.randint(0, 1200))).isoformat(),
                "rating": rating,
                "review": review,
            })
    return rows


def write_csv(path, header, rows):
    with open(path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=header)
        writer.writeheader()
        writer.writerows(rows)


def main():
    os.makedirs(DATA_DIR, exist_ok=True)
    recipes = build_recipes()
    interactions = build_interactions(recipes)

    write_csv(os.path.join(DATA_DIR, "recipes_sample.csv"), RECIPE_HEADER, recipes)
    write_csv(os.path.join(DATA_DIR, "interactions_sample.csv"), INTERACTION_HEADER, interactions)

    print(f"Wrote {len(recipes)} recipes and {len(interactions)} interactions to {DATA_DIR}")


if __name__ == "__main__":
    main()
