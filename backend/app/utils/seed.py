"""Seed the database from the sample CSV files on first startup.

Runs automatically when ``AUTO_SEED`` is true and the tables are empty. Loading
is idempotent: if recipes already exist, seeding is skipped so restarts are fast.
"""

import csv
from datetime import datetime

from sqlalchemy.orm import Session

from app.config import settings
from app.models.interaction import Interaction
from app.models.recipe import Recipe


def _parse_date(value):
    """Parse an ISO date string, returning None if it is missing/invalid."""
    if not value:
        return None
    try:
        return datetime.strptime(value.strip(), "%Y-%m-%d").date()
    except (ValueError, AttributeError):
        return None


def _to_int(value):
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return None


def _load_recipes(db: Session, path: str) -> int:
    count = 0
    with open(path, newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            db.add(Recipe(
                id=_to_int(row.get("id")),
                name=(row.get("name") or "").strip(),
                minutes=_to_int(row.get("minutes")),
                contributor_id=_to_int(row.get("contributor_id")),
                submitted=_parse_date(row.get("submitted")),
                tags=row.get("tags"),
                nutrition=row.get("nutrition"),
                n_steps=_to_int(row.get("n_steps")),
                steps=row.get("steps"),
                description=row.get("description"),
                ingredients=row.get("ingredients"),
                n_ingredients=_to_int(row.get("n_ingredients")),
            ))
            count += 1
    db.commit()
    return count


def _load_interactions(db: Session, path: str) -> int:
    count = 0
    with open(path, newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            db.add(Interaction(
                user_id=_to_int(row.get("user_id")),
                recipe_id=_to_int(row.get("recipe_id")),
                date=_parse_date(row.get("date")),
                rating=_to_int(row.get("rating")),
                review=row.get("review"),
            ))
            count += 1
    db.commit()
    return count


def seed_if_empty(db: Session) -> None:
    """Populate the database from the sample CSVs if it has no recipes yet."""
    if not settings.AUTO_SEED:
        return
    if db.query(Recipe).first() is not None:
        return  # already seeded

    try:
        recipes = _load_recipes(db, settings.SEED_RECIPES_PATH)
        interactions = _load_interactions(db, settings.SEED_INTERACTIONS_PATH)
        print(f"[seed] Inserted {recipes} recipes and {interactions} interactions.")
    except FileNotFoundError as exc:
        print(f"[seed] Sample data not found, skipping seed: {exc}")
