"""SQLAlchemy model for a recipe.

The columns mirror the Food.com ``RAW_recipes.csv`` layout. List-like columns
(``tags``, ``nutrition``, ``steps``, ``ingredients``) are stored as text exactly
as they appear in the dataset and parsed into real lists in the schema layer.
"""

from sqlalchemy import Column, Date, Integer, String, Text

from app.database.db import Base


class Recipe(Base):
    __tablename__ = "recipes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    minutes = Column(Integer)
    contributor_id = Column(Integer)
    submitted = Column(Date)
    tags = Column(Text)
    nutrition = Column(Text)
    n_steps = Column(Integer)
    steps = Column(Text)
    description = Column(Text)
    ingredients = Column(Text)
    n_ingredients = Column(Integer)
