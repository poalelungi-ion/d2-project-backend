"""
Database Configuration Module

This module sets up the SQLAlchemy engine, session maker, and base declarative class
for the SPA System. It connects to the PostgreSQL database specified by config.DATABASE_URL.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

import config

# Create the SQLAlchemy engine to manage connections.
engine = create_engine(config.DATABASE_URL)

# Create a configured "Session" class.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for all ORM models.
Base = declarative_base()


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
