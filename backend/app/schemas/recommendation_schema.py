"""Pydantic schemas for the recommendation endpoints."""

from typing import List, Optional

from pydantic import BaseModel, Field

from app.schemas.recipe_schema import RecipeSummary


class RecommendationRequest(BaseModel):
    """Preferences submitted by the user through the frontend form."""

    ingredients: List[str] = Field(
        default_factory=list,
        description="Ingredients the user has or wants to use.",
    )
    tags: List[str] = Field(
        default_factory=list,
        description="Desired tags such as 'vegetarian', 'quick', 'dinner'.",
    )
    exclude_ingredients: List[str] = Field(
        default_factory=list,
        description="Ingredients that must not appear in a recipe.",
    )
    max_minutes: Optional[int] = Field(
        default=None, description="Only recipes that cook within this many minutes."
    )
    min_rating: Optional[float] = Field(
        default=None, description="Minimum average user rating (0-5)."
    )
    limit: int = Field(default=10, ge=1, le=50, description="How many results to return.")


class ScoredRecipe(BaseModel):
    """A recommended recipe together with why it was chosen."""

    recipe: RecipeSummary
    score: float
    avg_rating: Optional[float] = None
    num_ratings: int = 0
    reasons: List[str] = []


class RecommendationResponse(BaseModel):
    """Full response for a recommendation query."""

    count: int
    results: List[ScoredRecipe]
