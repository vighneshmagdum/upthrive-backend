from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_auth_service, require_csrf
from app.core.config import settings
from app.core.security import new_csrf_token
from app.db.session import get_db
from app.schemas.auth import (
    AuthResponse,
    CsrfResponse,
    LoginRequest,
    MessageResponse,
    RegisterRequest,
)
from app.schemas.users import UserOut
from app.services.auth_service import (
    AuthService,
    DuplicateEmailError,
    InvalidCredentialsError,
    InvalidRefreshTokenError,
)


router = APIRouter(prefix="/auth", tags=["authentication"])
ACCESS_COOKIE = "upthrive_access"
REFRESH_COOKIE = "upthrive_refresh"
CSRF_COOKIE = "upthrive_csrf"
AUTH_COOKIE_PATH = settings.api_prefix + "/auth"


def _cookie_options() -> dict:
    return {
        "secure": settings.cookie_secure,
        "samesite": "lax",
        "domain": settings.auth_cookie_domain or None,
    }


def _set_session_cookies(
    response: Response, access_token: str, refresh_token: str
) -> None:
    options = _cookie_options()
    response.set_cookie(
        ACCESS_COOKIE,
        access_token,
        max_age=settings.access_token_minutes * 60,
        path=settings.api_prefix,
        httponly=True,
        **options,
    )
    response.set_cookie(
        REFRESH_COOKIE,
        refresh_token,
        max_age=settings.refresh_token_days * 24 * 60 * 60,
        path=AUTH_COOKIE_PATH,
        httponly=True,
        **options,
    )
    response.set_cookie(
        CSRF_COOKIE,
        new_csrf_token(),
        max_age=30 * 24 * 60 * 60,
        path="/",
        httponly=False,
        **options,
    )


def _clear_session_cookies(response: Response) -> None:
    options = _cookie_options()
    response.delete_cookie(ACCESS_COOKIE, path=settings.api_prefix, **options)
    response.delete_cookie(REFRESH_COOKIE, path=AUTH_COOKIE_PATH, **options)
    response.delete_cookie(CSRF_COOKIE, path="/", **options)


@router.get("/csrf", response_model=CsrfResponse)
def issue_csrf_token(request: Request, response: Response) -> CsrfResponse:
    token = request.cookies.get(CSRF_COOKIE) or new_csrf_token()
    response.set_cookie(
        CSRF_COOKIE,
        token,
        max_age=30 * 24 * 60 * 60,
        path="/",
        httponly=False,
        **_cookie_options(),
    )
    return CsrfResponse(csrf_token=token)


@router.post(
    "/register",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_csrf)],
)
def register(
    payload: RegisterRequest,
    request: Request,
    response: Response,
    service: AuthService = Depends(get_auth_service),
) -> AuthResponse:
    try:
        user = service.register(
            full_name=payload.full_name,
            email=str(payload.email),
            password=payload.password.get_secret_value(),
        )
    except DuplicateEmailError as exc:
        raise HTTPException(status_code=409, detail="An account with this email already exists.") from exc
    access_token, refresh_token = service.create_session(
        user, request.headers.get("user-agent")
    )
    _set_session_cookies(response, access_token, refresh_token)
    return AuthResponse(user=UserOut.model_validate(user))


@router.post(
    "/login",
    response_model=AuthResponse,
    dependencies=[Depends(require_csrf)],
)
def login(
    payload: LoginRequest,
    request: Request,
    response: Response,
    service: AuthService = Depends(get_auth_service),
) -> AuthResponse:
    try:
        user = service.authenticate(
            email=str(payload.email),
            password=payload.password.get_secret_value(),
        )
    except InvalidCredentialsError as exc:
        raise HTTPException(
            status_code=401,
            detail="Email or password is incorrect.",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    access_token, refresh_token = service.create_session(
        user, request.headers.get("user-agent")
    )
    _set_session_cookies(response, access_token, refresh_token)
    return AuthResponse(user=UserOut.model_validate(user))


@router.post(
    "/refresh",
    response_model=AuthResponse,
    dependencies=[Depends(require_csrf)],
)
def refresh(
    request: Request,
    response: Response,
    service: AuthService = Depends(get_auth_service),
) -> AuthResponse:
    try:
        user, access_token, refresh_token = service.rotate_refresh_token(
            request.cookies.get(REFRESH_COOKIE),
            request.headers.get("user-agent"),
        )
    except InvalidRefreshTokenError as exc:
        _clear_session_cookies(response)
        raise HTTPException(status_code=401, detail="Session expired. Please sign in again.") from exc

    _set_session_cookies(response, access_token, refresh_token)
    return AuthResponse(user=UserOut.model_validate(user))


@router.post(
    "/logout",
    response_model=MessageResponse,
    dependencies=[Depends(require_csrf)],
)
def logout(
    request: Request,
    response: Response,
    service: AuthService = Depends(get_auth_service),
) -> MessageResponse:
    service.revoke_refresh_token(request.cookies.get(REFRESH_COOKIE))
    _clear_session_cookies(response)
    return MessageResponse(message="Signed out.")
