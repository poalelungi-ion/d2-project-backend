"""
Application configuration.

Every value the backend needs from its environment is read here and nowhere
else, so deployment settings are visible in one file instead of being spread
across modules as literals. See .env.example for the deployable surface.
"""
import os

# Connection URL for the PostgreSQL instance. The default targets the "db"
# service defined in docker-compose.yml.
DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://spa_user:spa_password@db/spa_db"
)

# Shared secret expected in the Authorization header on mutating endpoints.
# The default preserves the value the client has always sent; override it in
# any environment that is not a local development machine.
API_TOKEN = os.getenv("API_TOKEN", "sse-staff-token")

# Origins permitted by the CORS middleware, as a comma-separated list.
# Defaults to "*" so a locally served client can talk to the API.
CORS_ORIGINS = [
    origin.strip()
    for origin in os.getenv("CORS_ORIGINS", "*").split(",")
    if origin.strip()
]

# Whether to populate an empty database with demonstration data at startup.
SEED_ON_STARTUP = os.getenv("SEED_ON_STARTUP", "true").lower() == "true"
