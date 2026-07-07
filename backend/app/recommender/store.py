"""In-memory cache for the fitted recommendation engine.

Fitting TF-IDF and building the graph on every request would be wasteful, so the
engine is built once from the database and reused. Call :func:`invalidate` after
importing new data to force a rebuild on the next request.
"""

import threading
from typing import Optional

from sqlalchemy.orm import Session

from app.recommender.engine import RecommendationEngine
from app.repositories.interaction_repository import InteractionRepository
from app.repositories.recipe_repository import RecipeRepository

_engine: Optional[RecommendationEngine] = None
_lock = threading.Lock()


def get_engine(db: Session) -> RecommendationEngine:
    """Return the cached engine, building it from the database if needed."""
    global _engine
    if _engine is None:
        with _lock:
            if _engine is None:  # double-checked locking
                recipes = RecipeRepository.get_all_for_engine(db)
                rating_stats = InteractionRepository.rating_stats(db)
                _engine = RecommendationEngine(recipes, rating_stats)
    return _engine


def invalidate() -> None:
    """Drop the cached engine so it is rebuilt on the next request."""
    global _engine
    with _lock:
        _engine = None
