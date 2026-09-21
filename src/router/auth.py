"""
Authentication Router (HTTP Controller).

Turns the auth service's results into responses: the access token goes in the
body for the client to hold in memory, the refresh token goes into an httpOnly
cookie the client's JavaScript can neither read nor forward.
"""
from fastapi import APIRouter, Cookie, Depends, Response, status
from sqlalchemy.orm import Session

from src.database import config
from src.database.connection import get_db
from src.database.models import User
from src.lib.auth.validator import get_current_user
from src.router.dto import LoginRequest, RegisterRequest, TokenResponse, UserResponse
from src.services import auth as auth_service
from src.services.auth import IssuedSession

router = APIRouter(prefix="/api/auth")


def _set_refresh_cookie(response: Response, token: str) -> None:
    """
    Writes the rotating refresh cookie.

    httponly keeps it out of document.cookie, so script injected into the page
    cannot read it. The path scopes it to this router, so it is not attached to
    course or student requests at all. max_age matches the token's own expiry,
    so a stale cookie is dropped by the browser rather than sent and refused.
    """
    response.set_cookie(
        key=config.REFRESH_COOKIE_NAME,
        value=token,
        httponly=True,
        secure=config.COOKIE_SECURE,
        samesite=config.COOKIE_SAMESITE,
        path=config.REFRESH_COOKIE_PATH,
        max_age=config.REFRESH_TOKEN_TTL_DAYS * 24 * 60 * 60,
    )


def _clear_refresh_cookie(response: Response) -> None:
    # Path must match the one it was set with, or the browser keeps the cookie.
    response.delete_cookie(
        key=config.REFRESH_COOKIE_NAME,
        path=config.REFRESH_COOKIE_PATH,
        httponly=True,
        secure=config.COOKIE_SECURE,
        samesite=config.COOKIE_SAMESITE,
    )


def _session_response(response: Response, session: IssuedSession) -> TokenResponse:
    _set_refresh_cookie(response, session.refresh_token)
    return TokenResponse(
        access_token=session.access_token,
        expires_in=session.expires_in,
        user=UserResponse.model_validate(session.user),
    )


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a university account",
)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    """
    Creates an account for a @uni-hildesheim.de address. The domain rule is
    enforced by the DTO, so a foreign address is refused with 422 before any
    database work happens. No session is opened here -- the client sends the
    same credentials to /login next.
    """
    return auth_service.register_user(db, payload)


@router.post("/login", response_model=TokenResponse, summary="Sign in")
def login(payload: LoginRequest, response: Response, db: Session = Depends(get_db)):
    """Verifies credentials, returns an access token and sets the refresh cookie."""
    session = auth_service.login(db, payload)
    return _session_response(response, session)


@router.post("/refresh", response_model=TokenResponse, summary="Rotate the session")
def refresh(
    response: Response,
    db: Session = Depends(get_db),
    spa_refresh_token: str | None = Cookie(default=None, alias=config.REFRESH_COOKIE_NAME),
):
    """
    Exchanges the refresh cookie for a new token pair. The old refresh token is
    revoked in the same call, so each one is good for exactly one use.
    """
    session = auth_service.refresh_session(db, spa_refresh_token)
    return _session_response(response, session)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT, summary="Sign out")
def logout(
    response: Response,
    db: Session = Depends(get_db),
    spa_refresh_token: str | None = Cookie(default=None, alias=config.REFRESH_COOKIE_NAME),
):
    """
    Revokes the current session server-side and clears the cookie. Deliberately
    unauthenticated: an expired access token must not prevent signing out.
    """
    auth_service.logout(db, spa_refresh_token)
    # The Set-Cookie written on the injected response is merged into the 204
    # FastAPI builds for a handler that returns nothing.
    _clear_refresh_cookie(response)


@router.get("/me", response_model=UserResponse, summary="Current account")
def me(current_user: User = Depends(get_current_user)):
    """Returns the account behind the presented access token."""
    return current_user
