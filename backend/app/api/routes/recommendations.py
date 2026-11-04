from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, require_csrf
from app.db.session import get_db
from app.models import User
from app.schemas.recommendations import (
    RecommendationList,
    RecommendationStatusUpdate,
)
from app.services.recommendation_service import RecommendationService


router = APIRouter(prefix="/recommendations", tags=["recommendations"])


@router.get("", response_model=RecommendationList)
def get_recommendations(
    limit: int = Query(default=5, ge=1, le=10),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> RecommendationList:
    return RecommendationList(**RecommendationService(db).list_for_user(user, limit))


@router.patch(
    "/{item_id}/status",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_csrf)],
)
def update_recommendation_status(
    item_id: str,
    payload: RecommendationStatusUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    try:
        RecommendationService(db).set_status(user, item_id, payload.status)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Recommendation not found.") from exc
