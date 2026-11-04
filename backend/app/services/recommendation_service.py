from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import RecommendationStatus, User
from app.recommendations.catalog import PATHS_BY_ID
from app.recommendations.engine import MODEL_NAME, rank_paths


class RecommendationService:
    def __init__(self, db: Session):
        self.db = db

    def list_for_user(self, user: User, limit: int) -> dict:
        statuses = {
            row.item_id: row.status
            for row in self.db.scalars(
                select(RecommendationStatus).where(RecommendationStatus.user_id == user.id)
            )
        }
        return {
            "items": rank_paths(user.profile, statuses, limit),
            "model": MODEL_NAME,
        }

    def set_status(self, user: User, item_id: str, status: str) -> None:
        if item_id not in PATHS_BY_ID:
            raise KeyError(item_id)
        record = self.db.get(RecommendationStatus, (user.id, item_id))
        if record is None:
            record = RecommendationStatus(user_id=user.id, item_id=item_id, status=status)
            self.db.add(record)
        else:
            record.status = status
        self.db.commit()
