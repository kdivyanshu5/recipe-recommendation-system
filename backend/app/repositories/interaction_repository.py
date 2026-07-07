"""Data-access layer for user interactions (ratings and reviews)."""

from typing import Dict, List, Tuple

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.interaction import Interaction


class InteractionRepository:
    """All database reads/writes for the ``interactions`` table."""

    @staticmethod
    def get_by_recipe(db: Session, recipe_id: int, limit: int = 20) -> List[Interaction]:
        return (
            db.query(Interaction)
            .filter(Interaction.recipe_id == recipe_id)
            .order_by(Interaction.date.desc())
            .limit(limit)
            .all()
        )

    @staticmethod
    def rating_stats(db: Session) -> Dict[int, Tuple[float, int]]:
        """Return ``{recipe_id: (average_rating, number_of_ratings)}``.

        Computed in a single grouped query so the recommender can blend
        popularity into its scores cheaply.
        """
        rows = (
            db.query(
                Interaction.recipe_id,
                func.avg(Interaction.rating),
                func.count(Interaction.id),
            )
            .group_by(Interaction.recipe_id)
            .all()
        )
        return {
            recipe_id: (float(avg_rating or 0.0), int(count))
            for recipe_id, avg_rating, count in rows
        }

    @staticmethod
    def top_recipes_for_user(db: Session, user_id: int, limit: int = 10) -> List[int]:
        """Recipe ids a user rated highly, best first. Used for personalization."""
        rows = (
            db.query(Interaction.recipe_id)
            .filter(Interaction.user_id == user_id)
            .order_by(Interaction.rating.desc())
            .limit(limit)
            .all()
        )
        return [row[0] for row in rows]
