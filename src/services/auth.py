"""
Authentication Domain Service.

Owns account creation, credential checking, and the refresh-token rotation
chain. Nothing here touches HTTP: the router turns what these functions return
into a response body and a Set-Cookie header.
"""
from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from src.database.models import RefreshToken, User
from src.lib.auth.passwords import hash_password, verify_password
from src.lib.auth.tokens import (
    REFRESH_TOKEN_TYPE,
    TokenError,
    create_access_token,
    create_refresh_token,
    decode_token,
)
from src.router.dto import LoginRequest, RegisterRequest

INVALID_CREDENTIALS = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Incorrect email or password",
    headers={"WWW-Authenticate": "Bearer"},
)

INVALID_SESSION = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Session expired. Please sign in again.",
    headers={"WWW-Authenticate": "Bearer"},
)


class IssuedSession:
    """An access token plus the refresh token the router turns into a cookie."""

    def __init__(self, user: User, access_token: str, expires_in: int, refresh_token: str):
        self.user = user
        self.access_token = access_token
        self.expires_in = expires_in
        self.refresh_token = refresh_token


def _issue_session(db: Session, user: User) -> IssuedSession:
    """Mints a fresh token pair and records the refresh token's jti."""
    access_token, expires_in = create_access_token(user.user_id)
    refresh_token, jti, expires_at = create_refresh_token(user.user_id)

    db.add(RefreshToken(jti=jti, user_id=user.user_id, expires_at=expires_at))
    db.commit()

    return IssuedSession(user, access_token, expires_in, refresh_token)


def register_user(db: Session, dto: RegisterRequest) -> User:
    """
    Creates an account. The DTO has already normalised the address and proven
    it sits in the university domain, so the only check left is uniqueness.
    """
    existing = db.query(User).filter(User.email == dto.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account already exists for this email address",
        )

    user = User(email=dto.email, name=dto.name, password_hash=hash_password(dto.password))
    try:
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    except Exception:
        db.rollback()
        raise


def login(db: Session, dto: LoginRequest) -> IssuedSession:
    """
    Verifies credentials and opens a session.

    A missing account still runs a bcrypt verification against a dummy hash so
    the response takes the same time either way -- otherwise the timing alone
    reveals which addresses are registered.
    """
    user = db.query(User).filter(User.email == dto.email).first()

    if user is None:
        verify_password(dto.password, _DUMMY_HASH)
        raise INVALID_CREDENTIALS

    if not verify_password(dto.password, user.password_hash):
        raise INVALID_CREDENTIALS

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This account has been deactivated",
        )

    return _issue_session(db, user)


def refresh_session(db: Session, refresh_token: str | None) -> IssuedSession:
    """
    Exchanges a refresh token for a new pair, invalidating the one presented.
    """
    if not refresh_token:
        raise INVALID_SESSION

    try:
        payload = decode_token(refresh_token, REFRESH_TOKEN_TYPE)
        user_id = int(payload["sub"])
        jti = payload["jti"]
    except (TokenError, KeyError, ValueError) as exc:
        raise INVALID_SESSION from exc

    stored = db.query(RefreshToken).filter(RefreshToken.jti == jti).first()
    if stored is None:
        raise INVALID_SESSION

    if stored.revoked_at is not None:
        revoke_all_for_user(db, stored.user_id)
        raise INVALID_SESSION

    if not stored.is_usable:
        raise INVALID_SESSION

    user = db.query(User).filter(User.user_id == user_id).first()
    if user is None or not user.is_active:
        raise INVALID_SESSION

    stored.revoked_at = datetime.now(timezone.utc)
    return _issue_session(db, user)


def logout(db: Session, refresh_token: str | None) -> None:
    """
    Ends the session the cookie names. Silent on an unusable token: the caller
    is being signed out either way, and there is nothing useful to report.
    """
    if not refresh_token:
        return
    try:
        jti = decode_token(refresh_token, REFRESH_TOKEN_TYPE)["jti"]
    except (TokenError, KeyError):
        return

    stored = db.query(RefreshToken).filter(RefreshToken.jti == jti).first()
    if stored and stored.revoked_at is None:
        stored.revoked_at = datetime.now(timezone.utc)
        db.commit()


def revoke_all_for_user(db: Session, user_id: int) -> None:
    """Drops every live session for one account."""
    now = datetime.now(timezone.utc)
    db.query(RefreshToken).filter(
        RefreshToken.user_id == user_id,
        RefreshToken.revoked_at.is_(None),
    ).update({RefreshToken.revoked_at: now}, synchronize_session=False)
    db.commit()


# A real bcrypt hash of a value nothing can log in with, used to keep the
# unknown-account path the same cost as the wrong-password path.
_DUMMY_HASH = hash_password("unusable-placeholder-password")
