"""Backward-compatible shim for config."""
from src.database.config import API_TOKEN, CORS_ORIGINS, DATABASE_URL, SEED_ON_STARTUP
__all__ = ["API_TOKEN", "CORS_ORIGINS", "DATABASE_URL", "SEED_ON_STARTUP"]
