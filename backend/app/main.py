"""FastAPI application entry point.

On startup it creates the tables, seeds the sample data if the database is empty,
and wires up the recipe and recommendation routers. The app stays responsive even
if the database is briefly unavailable at boot (Docker start order), because
seeding is retried with a short backoff.
"""

import time

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session

from app.config import settings
from app.database.db import Base, SessionLocal, engine, get_db
from app.models.interaction import Interaction  # noqa: F401 (registers the table)
from app.models.recipe import Recipe  # noqa: F401 (registers the table)
from app.recommender import quantum_demo, store
from app.routes.admin_routes import router as admin_router
from app.routes.recipe_routes import router as recipe_router
from app.routes.recommendation_routes import router as recommendation_router
from app.services.recipe_service import RecipeService
from app.utils.seed import seed_if_empty

app = FastAPI(title=settings.APP_NAME, version=settings.VERSION)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(recipe_router)
app.include_router(recommendation_router)
app.include_router(admin_router)


def _init_database(retries: int = 10, delay: float = 3.0) -> None:
    """Create tables and seed data, waiting for Postgres to accept connections."""
    for attempt in range(1, retries + 1):
        try:
            Base.metadata.create_all(bind=engine)
            db = SessionLocal()
            try:
                seed_if_empty(db)
            finally:
                db.close()
            return
        except OperationalError:
            print(f"[startup] Database not ready (attempt {attempt}/{retries}), retrying...")
            time.sleep(delay)
    print("[startup] Warning: database was not reachable during startup.")


@app.on_event("startup")
def on_startup() -> None:
    _init_database()
    # Reset any cached engine so it is rebuilt from freshly seeded data.
    store.invalidate()


@app.get("/", tags=["Health"])
def root():
    """Simple liveness message."""
    return {"message": f"{settings.APP_NAME} is running", "version": settings.VERSION}


@app.get("/health", tags=["Health"])
def health(db: Session = Depends(get_db)):
    """Report database connectivity, recipe count and quantum availability."""
    return {
        "status": "ok",
        "recipes": RecipeService.count_recipes(db),
        "quantum_enabled": settings.ENABLE_QUANTUM,
        "quantum_available": quantum_demo.is_available(),
    }
