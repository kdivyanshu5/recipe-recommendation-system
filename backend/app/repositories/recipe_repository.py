"""Data-access layer for recipes. Keeps SQL/ORM queries out of the services."""

from typing import List, Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.recipe import Recipe


class RecipeRepository:
    """All database reads/writes for the ``recipes`` table live here."""

    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 20) -> List[Recipe]:
        return db.query(Recipe).order_by(Recipe.id).offset(skip).limit(limit).all()

    @staticmethod
    def get_by_id(db: Session, recipe_id: int) -> Optional[Recipe]:
        return db.query(Recipe).filter(Recipe.id == recipe_id).first()

    @staticmethod
    def search_by_name(db: Session, term: str, limit: int = 20) -> List[Recipe]:
        pattern = f"%{term.lower()}%"
        return (
            db.query(Recipe)
            .filter(func.lower(Recipe.name).like(pattern))
            .order_by(Recipe.name)
            .limit(limit)
            .all()
        )

    @staticmethod
    def count(db: Session) -> int:
        return db.query(func.count(Recipe.id)).scalar() or 0

    @staticmethod
    def get_all_for_engine(db: Session) -> List[Recipe]:
        """Return every recipe. Used to build the in-memory recommender."""
        return db.query(Recipe).all()
