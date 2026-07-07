"""Business logic for recipe reads. Sits between the routes and the repository."""

from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.recipe import Recipe
from app.repositories.recipe_repository import RecipeRepository


class RecipeService:
    """Thin service layer so routes never touch the repository directly."""

    @staticmethod
    def list_recipes(db: Session, skip: int = 0, limit: int = 20) -> List[Recipe]:
        return RecipeRepository.get_all(db, skip=skip, limit=limit)

    @staticmethod
    def get_recipe(db: Session, recipe_id: int) -> Optional[Recipe]:
        return RecipeRepository.get_by_id(db, recipe_id)

    @staticmethod
    def search_recipes(db: Session, term: str, limit: int = 20) -> List[Recipe]:
        return RecipeRepository.search_by_name(db, term, limit=limit)

    @staticmethod
    def count_recipes(db: Session) -> int:
        return RecipeRepository.count(db)
