"""Tests for the recommendation engine.

These require the full backend dependencies (scikit-learn, networkx) and run
inside the Docker image or a local venv with requirements.txt installed:

    cd backend && pip install -r requirements.txt && pytest
"""

from types import SimpleNamespace

import pytest

from app.recommender.engine import RecommendationEngine
from app.schemas.recommendation_schema import RecommendationRequest


def make_recipe(recipe_id, name, minutes, ingredients, tags):
    """Build a lightweight stand-in for the SQLAlchemy Recipe model."""
    return SimpleNamespace(
        id=recipe_id,
        name=name,
        minutes=minutes,
        ingredients=str(ingredients),
        tags=str(tags),
        n_ingredients=len(ingredients),
    )


@pytest.fixture
def engine():
    recipes = [
        make_recipe(1, "chicken curry", 40, ["chicken", "onion", "curry powder"], ["dinner", "spicy"]),
        make_recipe(2, "veggie stir fry", 20, ["broccoli", "carrot", "soy sauce"], ["vegetarian", "quick"]),
        make_recipe(3, "chicken salad", 15, ["chicken", "lettuce", "tomato"], ["lunch", "quick"]),
        make_recipe(4, "chocolate cake", 60, ["flour", "sugar", "chocolate"], ["dessert", "sweet"]),
    ]
    # recipe 1 avg 4.5 (2 ratings), recipe 4 avg 5.0 (1 rating)
    rating_stats = {1: (4.5, 2), 4: (5.0, 1)}
    return RecommendationEngine(recipes, rating_stats)


def test_ingredient_match_ranks_relevant_recipe_first(engine):
    prefs = RecommendationRequest(ingredients=["chicken"], tags=["dinner"], limit=5)
    result = engine.recommend(prefs)
    assert result, "expected at least one recommendation"
    assert result[0]["recipe"].id == 1  # chicken + dinner recipe wins


def test_max_minutes_filter(engine):
    prefs = RecommendationRequest(ingredients=["chicken"], max_minutes=20, limit=5)
    result = engine.recommend(prefs)
    assert all(row["recipe"].minutes <= 20 for row in result)


def test_exclude_ingredient(engine):
    prefs = RecommendationRequest(tags=["quick"], exclude_ingredients=["chicken"], limit=5)
    result = engine.recommend(prefs)
    assert all("chicken" not in row["recipe"].ingredients for row in result)


def test_similar_returns_related_recipe(engine):
    result = engine.similar(1, limit=3)
    ids = [row["recipe"].id for row in result]
    assert 3 in ids  # chicken salad shares 'chicken' with chicken curry


def test_popular_orders_by_rating(engine):
    result = engine.popular(limit=4)
    assert result[0]["recipe"].id == 4  # 5.0 average rating
