"""HTTP routes for browsing recipes."""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.schemas.recipe_schema import RecipeDetail, RecipeSummary
from app.services.recipe_service import RecipeService

router = APIRouter(prefix="/recipes", tags=["Recipes"])


@router.get("/", response_model=List[RecipeSummary])
def list_recipes(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """Return a page of recipes."""
    return RecipeService.list_recipes(db, skip=skip, limit=limit)


@router.get("/search", response_model=List[RecipeSummary])
def search_recipes(
    q: str = Query(..., min_length=1, description="Text to match against recipe names."),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """Search recipes by name."""
    return RecipeService.search_recipes(db, q, limit=limit)


@router.get("/{recipe_id}", response_model=RecipeDetail)
def get_recipe(recipe_id: int, db: Session = Depends(get_db)):
    """Return the full detail of a single recipe."""
    recipe = RecipeService.get_recipe(db, recipe_id)
    if recipe is None:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return recipe
