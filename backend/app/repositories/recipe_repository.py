from sqlalchemy.orm import Session

from app.models.recipe import Recipe


class RecipeRepository:

    @staticmethod
    def get_all(db: Session):

        return db.query(Recipe).all()


    @staticmethod
    def get_by_id(db: Session, recipe_id: int):

        return db.query(Recipe).filter(
            Recipe.id == recipe_id
        ).first()