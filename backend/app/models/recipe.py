from sqlalchemy import Column, Integer, String, Text, Date

from app.database.db import Base


class Recipe(Base):
    __tablename__ = "recipes"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String, nullable=False)

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