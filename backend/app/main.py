from fastapi import FastAPI

from app.database.db import Base, engine
from app.models.recipe import Recipe
from app.models.interaction import Interaction
from app.routes.recipe_routes import router as recipe_router

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="FlavorGraph API",
    version="1.0.0"
)
app.include_router(recipe_router)

@app.get("/")
def root():
    return {"message": "FlavorGraph API is running!"}