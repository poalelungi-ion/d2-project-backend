"""Backward-compatible shim for application configuration."""
from src.database.config import (
    ACCESS_TOKEN_TTL_MINUTES,
    CORS_ORIGINS,
    DATABASE_URL,
    JWT_SECRET,
    REFRESH_TOKEN_TTL_DAYS,
    SEED_ON_STARTUP,
    UNIVERSITY_EMAIL_DOMAIN,
)
__all__ = [
    "ACCESS_TOKEN_TTL_MINUTES",
    "CORS_ORIGINS",
    "DATABASE_URL",
    "JWT_SECRET",
    "REFRESH_TOKEN_TTL_DAYS",
    "SEED_ON_STARTUP",
    "UNIVERSITY_EMAIL_DOMAIN",
]
