"""Import the FULL Food.com dataset into PostgreSQL.

Use this instead of the small sample when you want the complete data.

Data source (declared):
    Food.com Recipes and User Interactions
    https://www.kaggle.com/datasets/shuyangli94/food-com-recipes-and-user-interactions
    Files used: RAW_recipes.csv and RAW_interactions.csv

Usage (from the repository root, with the backend running or DB reachable):

    # 1. Download RAW_recipes.csv and RAW_interactions.csv from Kaggle
    # 2. Put them somewhere, e.g. ./dataset/
    # 3. Run:
    python backend/scripts/load_full_dataset.py \
        --recipes dataset/RAW_recipes.csv \
        --interactions dataset/RAW_interactions.csv \
        --limit-recipes 20000

The DB connection is read from the same environment variables the app uses
(DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME). When running on the host
against the Docker database, set DB_HOST=localhost.

``--limit-recipes`` keeps the import manageable; omit it to load everything
(this can take a while and use a lot of memory).
"""

import argparse
import os
import sys

# Make the ``app`` package importable when run as a standalone script.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pandas as pd  # noqa: E402

from app.database.db import Base, SessionLocal, engine  # noqa: E402
from app.models.interaction import Interaction  # noqa: E402
from app.models.recipe import Recipe  # noqa: E402


def load_recipes(session, path: str, limit: int | None) -> set:
    """Insert recipes and return the set of imported recipe ids."""
    frame = pd.read_csv(path)
    if limit:
        frame = frame.head(limit)

    imported_ids = set()
    records = []
    for row in frame.itertuples(index=False):
        data = row._asdict()
        recipe_id = int(data["id"])
        imported_ids.add(recipe_id)
        records.append(Recipe(
            id=recipe_id,
            name=str(data.get("name") or ""),
            minutes=_safe_int(data.get("minutes")),
            contributor_id=_safe_int(data.get("contributor_id")),
            submitted=_safe_date(data.get("submitted")),
            tags=str(data.get("tags")),
            nutrition=str(data.get("nutrition")),
            n_steps=_safe_int(data.get("n_steps")),
            steps=str(data.get("steps")),
            description=_safe_str(data.get("description")),
            ingredients=str(data.get("ingredients")),
            n_ingredients=_safe_int(data.get("n_ingredients")),
        ))

    session.bulk_save_objects(records)
    session.commit()
    print(f"Imported {len(records)} recipes.")
    return imported_ids


def load_interactions(session, path: str, valid_recipe_ids: set) -> None:
    """Insert interactions, skipping any that reference a missing recipe."""
    frame = pd.read_csv(path)
    records = []
    for row in frame.itertuples(index=False):
        data = row._asdict()
        recipe_id = _safe_int(data.get("recipe_id"))
        if valid_recipe_ids and recipe_id not in valid_recipe_ids:
            continue
        records.append(Interaction(
            user_id=_safe_int(data.get("user_id")),
            recipe_id=recipe_id,
            date=_safe_date(data.get("date")),
            rating=_safe_int(data.get("rating")),
            review=_safe_str(data.get("review")),
        ))
        if len(records) >= 50000:
            session.bulk_save_objects(records)
            session.commit()
            records = []
    if records:
        session.bulk_save_objects(records)
        session.commit()
    print("Imported interactions for the loaded recipes.")


def _safe_int(value):
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return None


def _safe_str(value):
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    return str(value)


def _safe_date(value):
    try:
        return pd.to_datetime(value).date()
    except (ValueError, TypeError):
        return None


def main():
    parser = argparse.ArgumentParser(description="Load the full Food.com dataset.")
    parser.add_argument("--recipes", required=True, help="Path to RAW_recipes.csv")
    parser.add_argument("--interactions", required=True, help="Path to RAW_interactions.csv")
    parser.add_argument(
        "--limit-recipes",
        type=int,
        default=None,
        help="Only import the first N recipes (recommended for a demo).",
    )
    args = parser.parse_args()

    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    try:
        recipe_ids = load_recipes(session, args.recipes, args.limit_recipes)
        load_interactions(session, args.interactions, recipe_ids)
        print("Done. Restart the backend or call POST /admin/rebuild to refresh the engine.")
    finally:
        session.close()


if __name__ == "__main__":
    main()
