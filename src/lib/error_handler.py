"""
Global Exception and Error Handlers.
Translates domain exceptions (such as optimistic locking StaleDataError) into standardized HTTP responses.
"""
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm.exc import StaleDataError


def register_error_handlers(app: FastAPI) -> None:
    """Registers global exception handlers on the FastAPI application."""

    @app.exception_handler(StaleDataError)
    async def stale_data_exception_handler(request: Request, exc: StaleDataError):
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"detail": "Data modified by another user. Please refresh."},
        )
