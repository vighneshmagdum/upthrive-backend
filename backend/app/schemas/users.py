from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


ExperienceLevel = Literal["beginner", "intermediate", "advanced"]


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    email: str
    full_name: str
    created_at: datetime


class ProfileOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    current_role: str
    experience_level: ExperienceLevel
    skills: list[str]
    interests: list[str]
    goals: list[str]
    weekly_hours: float


class UserMeResponse(BaseModel):
    user: UserOut
    profile: ProfileOut


class ProfileUpdate(BaseModel):
    full_name: str | None = Field(default=None, min_length=2, max_length=120)
    current_role: str | None = Field(default=None, max_length=120)
    experience_level: ExperienceLevel | None = None
    skills: list[str] | None = Field(default=None, max_length=30)
    interests: list[str] | None = Field(default=None, max_length=30)
    goals: list[str] | None = Field(default=None, max_length=20)
    weekly_hours: float | None = Field(default=None, ge=1, le=40)

    @field_validator("skills", "interests", "goals")
    @classmethod
    def normalize_terms(cls, value: list[str] | None) -> list[str] | None:
        if value is None:
            return None
        cleaned = []
        for term in value:
            term = term.strip()
            if not term or len(term) > 60:
                continue
            if term.casefold() not in {entry.casefold() for entry in cleaned}:
                cleaned.append(term)
        return cleaned
