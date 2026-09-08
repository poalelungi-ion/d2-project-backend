"""
Database Connection and Session Management.
Sets up SQLAlchemy engine, session maker, base declarative class, and dependency generator.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from src.database import config

engine = create_engine(config.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """
    FastAPI dependency yielding a database session per request.
    Ensures the session is cleanly closed on completion.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
