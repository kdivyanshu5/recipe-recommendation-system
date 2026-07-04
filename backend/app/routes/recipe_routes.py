from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session

from app.database.dependencies import get_db
from app.services.recipe_service import RecipeService

router = APIRouter(
    prefix="/recipes",
    tags=["Recipes"]
)


@router.get("/")
def get_recipes(
    db: Session = Depends(get_db)
):

    return RecipeService.get_all_recipes(db)


@router.get("/{recipe_id}")
def get_recipe(
    recipe_id: int,
    db: Session = Depends(get_db)
):

    return RecipeService.get_recipe(
        db,
        recipe_id
    )