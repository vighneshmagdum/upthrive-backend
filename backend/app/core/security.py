import secrets
from datetime import datetime, timedelta, timezone

import jwt
from pwdlib import PasswordHash

from app.core.config import settings


password_hash = PasswordHash.recommended()
_DUMMY_PASSWORD_HASH = password_hash.hash("not-a-real-upthrive-user-password")


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(password: str, stored_hash: str | None) -> bool:
    if stored_hash is None:
        password_hash.verify(password, _DUMMY_PASSWORD_HASH)
        return False
    return password_hash.verify(password, stored_hash)


def create_access_token(user_id: str) -> str:
    now = datetime.now(timezone.utc)
    claims = {
        "sub": user_id,
        "iss": settings.jwt_issuer,
        "iat": now,
        "exp": now + timedelta(minutes=settings.access_token_minutes),
        "jti": secrets.token_urlsafe(16),
        "type": "access",
    }
    return jwt.encode(claims, settings.jwt_secret, algorithm="HS256")


def decode_access_token(token: str) -> dict:
    claims = jwt.decode(
        token,
        settings.jwt_secret,
        algorithms=["HS256"],
        issuer=settings.jwt_issuer,
        options={"require": ["sub", "iss", "iat", "exp", "jti", "type"]},
    )
    if claims.get("type") != "access":
        raise jwt.InvalidTokenError("Wrong token type")
    return claims


def new_refresh_token() -> str:
    return secrets.token_urlsafe(48)


def hash_refresh_token(token: str) -> str:
    import hashlib

    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def new_csrf_token() -> str:
    return secrets.token_urlsafe(32)
