"""Administrative routes for maintenance tasks."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.recommender import store
from app.services.recipe_service import RecipeService

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.post("/rebuild")
def rebuild_engine(db: Session = Depends(get_db)):
    """Drop the cached recommender and rebuild it from the current database.

    Call this after importing the full dataset so recommendations use the new
    data without restarting the container.
    """
    store.invalidate()
    engine = store.get_engine(db)
    return {
        "status": "rebuilt",
        "recipes_loaded": len(engine.recipes),
        "total_recipes": RecipeService.count_recipes(db),
    }
