"""
Database Configuration Module

This module sets up the SQLAlchemy engine, session maker, and base declarative class
for the SPA System. It connects to the PostgreSQL database specified by config.DATABASE_URL.
"""
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker, declarative_base

import config

# Create the SQLAlchemy engine to manage connections.
engine = create_engine(config.DATABASE_URL)

# Create a configured "Session" class.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for all ORM models.
Base = declarative_base()


# Columns added after the first release, as (table, column, DDL type + default).
# `Base.metadata.create_all` creates missing tables but never alters existing
# ones, and there is no migration tool in the project, so a database created
# before one of these columns existed needs it added explicitly on startup.
_ADDED_COLUMNS = (
    ("exam_results", "attempt_type", "VARCHAR NOT NULL DEFAULT 'Other'"),
)


def ensure_schema():
    """Add post-release columns missing from an existing database. Idempotent."""
    inspector = inspect(engine)
    tables = set(inspector.get_table_names())
    with engine.begin() as conn:
        for table, column, ddl in _ADDED_COLUMNS:
            if table not in tables:
                continue  # create_all will build it complete.
            existing = {c["name"] for c in inspector.get_columns(table)}
            if column in existing:
                continue
            conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {column} {ddl}"))


def get_db():
    """
    Dependency generator for FastAPI routes.

    Yields a new database session per request and ensures it is closed
    safely after the request completes, guaranteeing clean connection management.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
