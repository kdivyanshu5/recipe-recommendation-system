"""SQLAlchemy model for a user interaction (a rating/review of a recipe)."""

from sqlalchemy import Column, Date, Integer, Text

from app.database.db import Base


class Interaction(Base):
    __tablename__ = "interactions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False, index=True)
    recipe_id = Column(Integer, nullable=False, index=True)
    date = Column(Date)
    rating = Column(Integer)
    review = Column(Text)
