from datetime import datetime, timedelta, timezone
from uuid import uuid4

from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import (
    create_access_token,
    hash_password,
    hash_refresh_token,
    new_refresh_token,
    verify_password,
)
from app.models import RefreshSession, User, UserProfile


class DuplicateEmailError(Exception):
    pass


class InvalidCredentialsError(Exception):
    pass


class InvalidRefreshTokenError(Exception):
    pass


class AuthService:
    def __init__(self, db: Session):
        self.db = db

    def register(self, *, full_name: str, email: str, password: str) -> User:
        normalized_email = email.strip().lower()
        if self.db.scalar(select(User.id).where(User.email == normalized_email)):
            raise DuplicateEmailError

        user = User(
            id=str(uuid4()),
            email=normalized_email,
            full_name=full_name.strip(),
            password_hash=hash_password(password),
        )
        profile = UserProfile(user_id=user.id)
        self.db.add_all([user, profile])
        try:
            self.db.commit()
        except IntegrityError as exc:
            self.db.rollback()
            raise DuplicateEmailError from exc
        self.db.refresh(user)
        return user

    def authenticate(self, *, email: str, password: str) -> User:
        user = self.db.scalar(select(User).where(User.email == email.strip().lower()))
        if not verify_password(password, user.password_hash if user else None):
            raise InvalidCredentialsError
        return user

    def create_session(self, user: User, user_agent: str | None) -> tuple[str, str]:
        refresh_token = new_refresh_token()
        session = RefreshSession(
            id=str(uuid4()),
            user_id=user.id,
            token_hash=hash_refresh_token(refresh_token),
            expires_at=datetime.now(timezone.utc)
            + timedelta(days=settings.refresh_token_days),
            user_agent=(user_agent or "")[:512] or None,
        )
        self.db.add(session)
        self.db.commit()
        return create_access_token(user.id), refresh_token

    def rotate_refresh_token(
        self, token: str | None, user_agent: str | None
    ) -> tuple[User, str, str]:
        if not token:
            raise InvalidRefreshTokenError

        current = self.db.scalar(
            select(RefreshSession)
            .where(RefreshSession.token_hash == hash_refresh_token(token))
            .with_for_update()
        )
        if current is None:
            raise InvalidRefreshTokenError

        now = datetime.now(timezone.utc)
        expires_at = current.expires_at
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)

        if current.revoked_at is not None:
            self.db.execute(
                update(RefreshSession)
                .where(
                    RefreshSession.user_id == current.user_id,
                    RefreshSession.revoked_at.is_(None),
                )
                .values(revoked_at=now)
            )
            self.db.commit()
            raise InvalidRefreshTokenError
        if expires_at <= now:
            current.revoked_at = now
            self.db.commit()
            raise InvalidRefreshTokenError

        user = self.db.get(User, current.user_id)
        if user is None:
            current.revoked_at = now
            self.db.commit()
            raise InvalidRefreshTokenError

        current.revoked_at = now
        next_refresh = new_refresh_token()
        next_session = RefreshSession(
            id=str(uuid4()),
            user_id=user.id,
            token_hash=hash_refresh_token(next_refresh),
            expires_at=now + timedelta(days=settings.refresh_token_days),
            user_agent=(user_agent or "")[:512] or None,
        )
        self.db.add(next_session)
        self.db.commit()
        return user, create_access_token(user.id), next_refresh

    def revoke_refresh_token(self, token: str | None) -> None:
        if not token:
            return
        session = self.db.scalar(
            select(RefreshSession).where(
                RefreshSession.token_hash == hash_refresh_token(token),
                RefreshSession.revoked_at.is_(None),
            )
        )
        if session is not None:
            session.revoked_at = datetime.now(timezone.utc)
            self.db.commit()


class UserService:
    def __init__(self, db: Session):
        self.db = db

    def get(self, user_id: str) -> User | None:
        return self.db.get(User, user_id)

    def update_profile(self, user: User, changes: dict) -> User:
        profile = user.profile
        if profile is None:
            profile = UserProfile(user_id=user.id)
            user.profile = profile
            self.db.add(profile)

        if "full_name" in changes:
            user.full_name = changes.pop("full_name").strip()
        for key, value in changes.items():
            setattr(profile, key, value)
        self.db.commit()
        self.db.refresh(user)
        self.db.refresh(profile)
        return user
