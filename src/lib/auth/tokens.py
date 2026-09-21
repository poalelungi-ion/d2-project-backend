"""
JWT Issuing and Decoding.

Two token types share one signing key and are told apart by their "typ" claim,
which is checked on decode -- a refresh token must never be usable as a bearer
token on a data endpoint, and vice versa.

  access  -- minutes long, returned in the response body, kept in client
             memory, replayed as "Authorization: Bearer ...".
  refresh -- days long, delivered as an httpOnly cookie, carries a "jti" that
             matches a refresh_tokens row so it can be revoked.
"""
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

import jwt

from src.database import config

ACCESS_TOKEN_TYPE = "access"
REFRESH_TOKEN_TYPE = "refresh"


class TokenError(Exception):
    """Raised when a token is absent, malformed, expired, or of the wrong type."""


def _encode(subject: int, token_type: str, lifetime: timedelta, jti: str) -> tuple[str, datetime]:
    issued_at = datetime.now(timezone.utc)
    expires_at = issued_at + lifetime
    payload = {
        "sub": str(subject),
        "typ": token_type,
        "jti": jti,
        "iss": config.JWT_ISSUER,
        "iat": issued_at,
        "exp": expires_at,
    }
    token = jwt.encode(payload, config.JWT_SECRET, algorithm=config.JWT_ALGORITHM)
    return token, expires_at


def create_access_token(user_id: int) -> tuple[str, int]:
    """Returns the signed access token and its lifetime in seconds."""
    lifetime = timedelta(minutes=config.ACCESS_TOKEN_TTL_MINUTES)
    token, _ = _encode(user_id, ACCESS_TOKEN_TYPE, lifetime, uuid.uuid4().hex)
    return token, int(lifetime.total_seconds())


def create_refresh_token(user_id: int) -> tuple[str, str, datetime]:
    """Returns the signed refresh token, its jti, and its expiry instant."""
    jti = uuid.uuid4().hex
    lifetime = timedelta(days=config.REFRESH_TOKEN_TTL_DAYS)
    token, expires_at = _encode(user_id, REFRESH_TOKEN_TYPE, lifetime, jti)
    return token, jti, expires_at


def decode_token(token: str, expected_type: str) -> dict[str, Any]:
    """
    Verifies signature, issuer, expiry and token type.

    Every failure mode collapses into TokenError: the caller answers 401
    regardless, and a more specific message would only tell an attacker which
    part of a forged token to fix.
    """
    try:
        payload = jwt.decode(
            token,
            config.JWT_SECRET,
            algorithms=[config.JWT_ALGORITHM],
            issuer=config.JWT_ISSUER,
            options={"require": ["exp", "iat", "sub", "typ", "jti"]},
        )
    except jwt.PyJWTError as exc:
        raise TokenError("Invalid or expired token") from exc

    if payload.get("typ") != expected_type:
        raise TokenError("Token is not valid for this operation")
    return payload
