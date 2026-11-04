from typing import Literal

from pydantic import BaseModel, Field


RecommendationStatusValue = Literal["saved", "completed", "dismissed"]


class RecommendationOut(BaseModel):
    id: str
    title: str
    summary: str
    category: str
    difficulty: str
    estimated_weeks: int
    weekly_hours: int
    skills: list[str]
    steps: list[str]
    score: int
    explanation: str
    status: Literal["saved"] | None = None


class RecommendationList(BaseModel):
    items: list[RecommendationOut]
    model: str


class RecommendationStatusUpdate(BaseModel):
    status: RecommendationStatusValue = Field(description="Save, complete, or dismiss this path.")
