from pydantic import BaseModel


class RecipeResponse(BaseModel):

    id: int

    name: str

    minutes: int

    class Config:
        from_attributes = True