"""Business logic for recommendations.

Turns raw engine output (dicts holding ORM recipes) into the Pydantic schemas
the API returns, and coordinates the optional quantum re-ranking demo.
"""

from typing import List

from sqlalchemy.orm import Session

from app.recommender import quantum_demo, store
from app.schemas.recipe_schema import RecipeSummary
from app.schemas.recommendation_schema import (
    RecommendationRequest,
    RecommendationResponse,
    ScoredRecipe,
)


def _to_scored(rows: List[dict]) -> List[ScoredRecipe]:
    """Map engine result rows onto the ScoredRecipe schema."""
    return [
        ScoredRecipe(
            recipe=RecipeSummary.model_validate(row["recipe"]),
            score=row["score"],
            avg_rating=row.get("avg_rating"),
            num_ratings=row.get("num_ratings", 0),
            reasons=row.get("reasons", []),
        )
        for row in rows
    ]


class RecommendationService:
    """Coordinates the recommendation engine for the routes."""

    @staticmethod
    def recommend(db: Session, prefs: RecommendationRequest) -> RecommendationResponse:
        engine = store.get_engine(db)
        rows = engine.recommend(prefs)
        results = _to_scored(rows)
        return RecommendationResponse(count=len(results), results=results)

    @staticmethod
    def similar(db: Session, recipe_id: int, limit: int) -> RecommendationResponse:
        engine = store.get_engine(db)
        rows = engine.similar(recipe_id, limit=limit)
        results = _to_scored(rows)
        return RecommendationResponse(count=len(results), results=results)

    @staticmethod
    def popular(db: Session, limit: int) -> RecommendationResponse:
        engine = store.get_engine(db)
        rows = engine.popular(limit=limit)
        results = _to_scored(rows)
        return RecommendationResponse(count=len(results), results=results)

    @staticmethod
    def quantum_recommend(
        db: Session, prefs: RecommendationRequest
    ) -> RecommendationResponse:
        """Optional demo: get a larger candidate set then re-rank for diversity."""
        engine = store.get_engine(db)

        # Ask the engine for more candidates than requested, then let the
        # quantum optimiser choose a diverse subset.
        widened = prefs.model_copy(update={"limit": min(prefs.limit * 3, 12)})
        candidates = engine.recommend(widened)
        if not candidates:
            return RecommendationResponse(count=0, results=[])

        def similarity(i: int, j: int) -> float:
            return engine.content_similarity(candidates[i]["index"], candidates[j]["index"])

        chosen = quantum_demo.quantum_rerank(candidates, k=prefs.limit, similarity=similarity)
        results = _to_scored(chosen)
        return RecommendationResponse(count=len(results), results=results)
