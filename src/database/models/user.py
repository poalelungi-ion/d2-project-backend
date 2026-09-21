"""
User and RefreshToken ORM Models.

A user row never holds a password -- only a bcrypt hash, which embeds its own
per-row salt. Refresh tokens are recorded rather than trusted blindly, so a
session can be ended server-side on logout and a replayed token can be caught.
"""
from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from src.database.connection import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    # Stored lower-cased so "A.Musterfrau@..." and "a.musterfrau@..." are one
    # account and the unique constraint actually holds.
    email = Column(String, nullable=False, unique=True, index=True)
    name = Column(String, nullable=False)
    # bcrypt output: "$2b$<rounds>$<22-char salt><31-char digest>".
    password_hash = Column(String, nullable=False)
    is_active = Column(Boolean, nullable=False, default=True, server_default="true")
    created_at = Column(DateTime(timezone=True), nullable=False, default=_utcnow)

    # [REQ-CONCURRENCY-01] Version tracking for optimistic locking
    version = Column(Integer, nullable=False, default=1)

    __mapper_args__ = {
        "version_id_col": version
    }

    refresh_tokens = relationship(
        "RefreshToken", back_populates="user", cascade="all, delete-orphan"
    )


class RefreshToken(Base):
    """
    One issued refresh token, identified by the `jti` claim of the JWT handed
    to the browser. The token string itself is not stored: possession of the
    cookie is what authenticates, and this row only records whether that
    particular issuance is still allowed to be exchanged.
    """
    __tablename__ = "refresh_tokens"

    token_id = Column(Integer, primary_key=True, index=True)
    jti = Column(String, nullable=False, unique=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True)
    issued_at = Column(DateTime(timezone=True), nullable=False, default=_utcnow)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    # Set when the token is rotated away, logged out, or revoked in bulk after
    # a replay. A non-null value means the token must never be accepted again.
    revoked_at = Column(DateTime(timezone=True), nullable=True)

    user = relationship("User", back_populates="refresh_tokens")

    @property
    def is_usable(self) -> bool:
        if self.revoked_at is not None:
            return False
        expires_at = self.expires_at
        # SQLite hands back naive datetimes even for timezone=True columns.
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        return expires_at > _utcnow()
