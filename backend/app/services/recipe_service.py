from sqlalchemy.orm import Session

from app.repositories.recipe_repository import RecipeRepository


class RecipeService:

    @staticmethod
    def get_all_recipes(db: Session):

        return RecipeRepository.get_all(db)


    @staticmethod
    def get_recipe(db: Session, recipe_id: int):

        return RecipeRepository.get_by_id(
            db,
            recipe_id
        )