from sqlalchemy import Column, Integer, Text, Date

from app.database.db import Base


class Interaction(Base):
    __tablename__ = "interactions"

    id = Column(Integer, primary_key=True, autoincrement=True)

    user_id = Column(Integer, nullable=False)

    recipe_id = Column(Integer, nullable=False)

    date = Column(Date)

    rating = Column(Integer)

    review = Column(Text)