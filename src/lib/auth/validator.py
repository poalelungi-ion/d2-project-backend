"""
Authentication Dependency.

The HTTPBearer scheme is kept so the Swagger UI "Authorize" modal still works
-- paste an access token from POST /api/auth/login into it.
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from src.database.connection import get_db
from src.database.models import User
from src.lib.auth.tokens import ACCESS_TOKEN_TYPE, TokenError, decode_token

security = HTTPBearer(auto_error=False)

UNAUTHORIZED = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Not authenticated",
    headers={"WWW-Authenticate": "Bearer"},
)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    """
    Resolves the bearer access token to the User row it names.
    """
    if not credentials or credentials.scheme.lower() != "bearer":
        raise UNAUTHORIZED

    try:
        payload = decode_token(credentials.credentials, ACCESS_TOKEN_TYPE)
        user_id = int(payload["sub"])
    except (TokenError, KeyError, ValueError) as exc:
        raise UNAUTHORIZED from exc

    user = db.query(User).filter(User.user_id == user_id).first()
    if user is None or not user.is_active:
        raise UNAUTHORIZED
    return user
