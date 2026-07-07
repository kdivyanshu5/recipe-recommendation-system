"""Pydantic schemas describing recipe responses sent to the frontend."""

from typing import List, Optional

from pydantic import BaseModel, field_validator

from app.utils.parsing import parse_float_list, parse_list


class RecipeSummary(BaseModel):
    """A light-weight recipe view used in lists and recommendation results."""

    id: int
    name: str
    minutes: Optional[int] = None
    n_ingredients: Optional[int] = None
    tags: List[str] = []
    ingredients: List[str] = []

    @field_validator("tags", "ingredients", mode="before")
    @classmethod
    def _split_lists(cls, value):
        return parse_list(value)

    class Config:
        from_attributes = True


class RecipeDetail(RecipeSummary):
    """The full recipe view returned when a single recipe is requested."""

    contributor_id: Optional[int] = None
    submitted: Optional[str] = None
    n_steps: Optional[int] = None
    steps: List[str] = []
    nutrition: List[float] = []
    description: Optional[str] = None

    @field_validator("steps", mode="before")
    @classmethod
    def _split_steps(cls, value):
        return parse_list(value)

    @field_validator("nutrition", mode="before")
    @classmethod
    def _split_nutrition(cls, value):
        return parse_float_list(value)

    @field_validator("submitted", mode="before")
    @classmethod
    def _stringify_date(cls, value):
        return None if value is None else str(value)

    class Config:
        from_attributes = True
