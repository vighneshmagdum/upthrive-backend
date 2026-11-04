from fastapi import APIRouter, Depends

from app.api.dependencies import get_current_user, get_user_service
from app.schemas.users import ProfileUpdate, UserMeResponse
from app.services.auth_service import UserService
from app.models import User


router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserMeResponse)
def get_me(user: User = Depends(get_current_user)) -> UserMeResponse:
    return UserMeResponse(user=user, profile=user.profile)


@router.patch("/me/profile", response_model=UserMeResponse)
def update_profile(
    payload: ProfileUpdate,
    user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
) -> UserMeResponse:
    updated = service.update_profile(
        user, payload.model_dump(exclude_unset=True, exclude_none=True)
    )
    return UserMeResponse(user=updated, profile=updated.profile)
