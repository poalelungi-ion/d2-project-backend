"""
Database Configuration Module

This module sets up the SQLAlchemy engine, session maker, and base declarative class
for the SPA System. It connects to the PostgreSQL database specified by the DATABASE_URL.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

# Define the connection URL. Defaults to the docker-compose postgres service.
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://spa_user:spa_password@db/spa_db")

# Create the SQLAlchemy engine to manage connections.
engine = create_engine(DATABASE_URL)

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

