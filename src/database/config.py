"""
Application configuration module.
Reads environment variables for database connection, API authentication tokens, and CORS.
"""
import os

DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://spa_user:spa_password@db/spa_db"
)

API_TOKEN = os.getenv("API_TOKEN", "sse-staff-token")

CORS_ORIGINS = [
    origin.strip()
    for origin in os.getenv("CORS_ORIGINS", "*").split(",")
    if origin.strip()
]

SEED_ON_STARTUP = os.getenv("SEED_ON_STARTUP", "true").lower() == "true"
