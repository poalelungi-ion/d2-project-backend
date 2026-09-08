"""
Authentication and Authorization Validator.
Defines the HTTPBearer security dependency for Swagger UI testability and protects mutating endpoints.
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.database import config

# HTTPBearer enables the Swagger UI Authorize modal with Bearer scheme
security = HTTPBearer(auto_error=False)


def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> bool:
    """
    Validates that the request Authorization header contains a valid Bearer token matching config.API_TOKEN.
    Works seamlessly both in production/client requests and in Swagger UI interactive testing.
    """
    if not credentials or credentials.scheme.lower() != "bearer" or credentials.credentials != config.API_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized: Invalid or missing bearer token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return True
