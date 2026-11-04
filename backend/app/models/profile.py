from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, JSON, String, func, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class UserProfile(Base):
    __tablename__ = "user_profiles"

    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    current_role: Mapped[str] = mapped_column(String(120), default="", nullable=False)
    experience_level: Mapped[str] = mapped_column(String(24), default="beginner", nullable=False)
    skills: Mapped[list[str]] = mapped_column(JSON, default=list, server_default=text("'[]'"), nullable=False)
    interests: Mapped[list[str]] = mapped_column(JSON, default=list, server_default=text("'[]'"), nullable=False)
    goals: Mapped[list[str]] = mapped_column(JSON, default=list, server_default=text("'[]'"), nullable=False)
    weekly_hours: Mapped[float] = mapped_column(Float, default=4, server_default="4", nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    user: Mapped["User"] = relationship(back_populates="profile")
