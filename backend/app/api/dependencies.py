from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import decode_access_token
from app.db.session import get_db
from app.models import User
from app.services.auth_service import AuthService, UserService
import jwt
import secrets


def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    return AuthService(db)


def get_user_service(db: Session = Depends(get_db)) -> UserService:
    return UserService(db)


def require_csrf(request: Request) -> None:
    cookie_token = request.cookies.get("upthrive_csrf")
    header_token = request.headers.get("X-CSRF-Token")
    if (
        not cookie_token
        or not header_token
        or not secrets.compare_digest(cookie_token, header_token)
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="CSRF validation failed. Refresh the page and try again.",
        )


def get_current_user(
    request: Request, db: Session = Depends(get_db)
) -> User:
    token = request.cookies.get("upthrive_access")
    if not token:
        raise HTTPException(status_code=401, detail="Authentication required.")
    try:
        claims = decode_access_token(token)
    except jwt.InvalidTokenError as exc:
        raise HTTPException(status_code=401, detail="Session expired.") from exc

    user = db.get(User, claims["sub"])
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication required.")
    return user
