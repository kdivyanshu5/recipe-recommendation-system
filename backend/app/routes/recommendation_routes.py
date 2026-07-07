"""HTTP routes for the recommendation features."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.recommender import quantum_demo
from app.schemas.recommendation_schema import (
    RecommendationRequest,
    RecommendationResponse,
)
from app.services.recommendation_service import RecommendationService

router = APIRouter(prefix="/recommend", tags=["Recommendations"])


@router.post("/", response_model=RecommendationResponse)
def recommend(prefs: RecommendationRequest, db: Session = Depends(get_db)):
    """Recommend recipes that match the user's submitted preferences."""
    return RecommendationService.recommend(db, prefs)


@router.get("/popular", response_model=RecommendationResponse)
def popular(limit: int = Query(10, ge=1, le=50), db: Session = Depends(get_db)):
    """Return the most popular recipes (highest rated, most rated)."""
    return RecommendationService.popular(db, limit=limit)


@router.get("/similar/{recipe_id}", response_model=RecommendationResponse)
def similar(
    recipe_id: int,
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
):
    """Return recipes similar to the given recipe ('more like this')."""
    response = RecommendationService.similar(db, recipe_id, limit=limit)
    if response.count == 0:
        raise HTTPException(status_code=404, detail="Recipe not found or has no matches")
    return response


@router.post("/quantum", response_model=RecommendationResponse)
def quantum(prefs: RecommendationRequest, db: Session = Depends(get_db)):
    """Optional demo: diversity-aware re-ranking with QAOA (Qiskit).

    Returns 503 with instructions when the quantum extra is disabled or missing.
    """
    try:
        return RecommendationService.quantum_recommend(db, prefs)
    except quantum_demo.QuantumUnavailable as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
