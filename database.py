"""Backward-compatible shim for database connection."""
from src.database.connection import Base, SessionLocal, engine, get_db
__all__ = ["Base", "SessionLocal", "engine", "get_db"]
