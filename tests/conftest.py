"""
Test configuration.

The application reads its database URL at import time, so the override has to
be in place before any test module imports main. Pointing at SQLite lets the
suite run without a PostgreSQL instance, and seeding is disabled so tests
start from an empty schema.
"""
import os

os.environ.setdefault("DATABASE_URL", "sqlite:///./test.db")
os.environ.setdefault("SEED_ON_STARTUP", "false")
