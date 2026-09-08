"""
SPA System Backend API Application.
Main FastAPI application entry point. Configures lifespan, OpenAPI metadata,
Swagger UI testing security schemes, CORS middleware, global error handling, and router registration.
"""
from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi

from src.database import config
from src.database.connection import Base, engine
from src.database.seed import seed_db
from src.lib.error_handler import register_error_handlers
from src.router.router import api_router

logger = logging.getLogger("uvicorn.error")


def run_migrations():
    """Runs database migrations to ensure schema is always up to date on startup."""
    try:
        from alembic.config import Config
        from alembic import command
        alembic_cfg = Config("alembic.ini")
        command.upgrade(alembic_cfg, "head")
        logger.info("Alembic migrations applied successfully.")
    except Exception as e:
        logger.warning(f"Alembic auto-upgrade notice: {e}. Ensuring tables exist via Base.metadata...")
        Base.metadata.create_all(bind=engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    Runs database schema migrations and seeds baseline data on startup.
    """
    run_migrations()
    if config.SEED_ON_STARTUP:
        seed_db()
    yield


app = FastAPI(
    title="Study Progress Analysis API",
    description="Backend API for the Study Progress Analysis (SPA) System with Swagger testing support.",
    version="2.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Register CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register global error handlers
register_error_handlers(app)

# Mount all routers
app.include_router(api_router)


@app.get("/", summary="Service Health & Welcome")
def read_root():
    return {"message": "Welcome to the SPA Backend API!"}


def custom_openapi():
    """Custom OpenAPI schema that explicitly registers HTTPBearer security for Swagger UI testing."""
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    openapi_schema["components"] = openapi_schema.get("components", {})
    openapi_schema["components"]["securitySchemes"] = {
        "HTTPBearer": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "Token",
            "description": "Enter the API Bearer Token (default: sse-staff-token) to authorize Swagger requests.",
        }
    }
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi
