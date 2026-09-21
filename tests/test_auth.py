"""
Tests for account security: password storage, the login form's contract, the
university email rule, and the access/refresh token lifecycle.

These run with the authentication override from tests.test_api lifted, so the
real get_current_user dependency and the real token decoding are exercised.
"""
import pytest

from src.database import config
from src.database.models import RefreshToken, User
from src.lib.auth.passwords import hash_password, verify_password
from src.lib.auth.tokens import (
    ACCESS_TOKEN_TYPE,
    REFRESH_TOKEN_TYPE,
    TokenError,
    create_refresh_token,
    decode_token,
)
from tests.test_api import TestingSessionLocal, anonymous_client

EMAIL = "a.musterfrau@uni-hildesheim.de"
PASSWORD = "correct-horse-battery"


@pytest.fixture
def api():
    """
    The shared TestClient with the auth override removed for the test.

    Accounts and sessions are cleared first: the schema reset in test_api's
    fixture does not cover this module, and a leftover account would turn a
    registration into a 409.
    """
    db = TestingSessionLocal()
    try:
        db.query(RefreshToken).delete()
        db.query(User).delete()
        db.commit()
    finally:
        db.close()

    with anonymous_client() as client:
        client.cookies.clear()
        yield client
        client.cookies.clear()


def register(client, email=EMAIL, password=PASSWORD, name="Anna Musterfrau"):
    return client.post(
        "/api/auth/register", json={"email": email, "name": name, "password": password}
    )


def login(client, email=EMAIL, password=PASSWORD):
    return client.post("/api/auth/login", json={"email": email, "password": password})


# --- Password storage -------------------------------------------------------

def test_password_is_stored_as_a_bcrypt_hash_not_plaintext(api):
    assert register(api).status_code == 201

    db = TestingSessionLocal()
    try:
        user = db.query(User).filter(User.email == EMAIL).one()
        assert PASSWORD not in user.password_hash
        assert user.password_hash.startswith("$2b$")
        assert verify_password(PASSWORD, user.password_hash)
    finally:
        db.close()


def test_equal_passwords_get_different_hashes():
    """Each hash carries its own salt, so a stolen table cannot be de-duplicated."""
    first = hash_password(PASSWORD)
    second = hash_password(PASSWORD)
    assert first != second
    assert verify_password(PASSWORD, first) and verify_password(PASSWORD, second)


def test_verify_password_rejects_a_wrong_password_and_a_broken_hash():
    stored = hash_password(PASSWORD)
    assert not verify_password("something-else-entirely", stored)
    assert not verify_password(PASSWORD, "not-a-bcrypt-hash")


def test_password_past_the_bcrypt_ceiling_is_refused_rather_than_truncated(api):
    """
    bcrypt ignores everything past 72 bytes. Accepting a longer password would
    silently make every suffix equivalent, so registration rejects it instead.
    """
    too_long = "x" * (config.MAX_PASSWORD_BYTES + 1)
    assert register(api, password=too_long).status_code == 422


def test_short_password_is_refused(api):
    assert register(api, password="short").status_code == 422


# --- University email rule --------------------------------------------------

@pytest.mark.parametrize(
    "email",
    [
        "someone@gmail.com",
        "someone@uni-hildesheim.com",
        # Ends with the domain as a substring but is not in it.
        "someone@notuni-hildesheim.de",
        # The domain appears before the real one; only the final @-part counts.
        "someone@uni-hildesheim.de.attacker.example",
    ],
)
def test_registration_rejects_addresses_outside_the_university_domain(api, email):
    assert register(api, email=email).status_code == 422


def test_registration_normalises_case_and_surrounding_whitespace(api):
    response = register(api, email="  A.Musterfrau@Uni-Hildesheim.DE  ")
    assert response.status_code == 201
    assert response.json()["email"] == EMAIL


def test_registration_refuses_a_duplicate_address(api):
    assert register(api).status_code == 201
    duplicate = register(api, email=EMAIL.upper())
    assert duplicate.status_code == 409


# --- Login ------------------------------------------------------------------

def test_login_returns_an_access_token_and_sets_an_httponly_refresh_cookie(api):
    register(api)
    response = login(api)
    assert response.status_code == 200

    body = response.json()
    assert body["token_type"] == "bearer"
    assert body["expires_in"] == config.ACCESS_TOKEN_TTL_MINUTES * 60
    assert body["user"]["email"] == EMAIL
    # The refresh token must never reach JavaScript.
    assert "refresh_token" not in body

    cookie_header = response.headers["set-cookie"]
    assert config.REFRESH_COOKIE_NAME in cookie_header
    assert "HttpOnly" in cookie_header
    assert f"Path={config.REFRESH_COOKIE_PATH}" in cookie_header


def test_login_is_case_insensitive_on_the_address(api):
    register(api)
    assert login(api, email="A.MUSTERFRAU@UNI-HILDESHEIM.DE").status_code == 200


def test_login_rejects_a_wrong_password(api):
    register(api)
    assert login(api, password="not-the-password").status_code == 401


def test_login_gives_the_same_answer_for_an_unknown_account(api):
    """An unknown address and a wrong password are indistinguishable."""
    register(api)
    unknown = login(api, email="nobody@uni-hildesheim.de")
    wrong = login(api, password="not-the-password")
    assert unknown.status_code == wrong.status_code == 401
    assert unknown.json()["detail"] == wrong.json()["detail"]


def test_a_deactivated_account_cannot_sign_in(api):
    register(api)
    db = TestingSessionLocal()
    try:
        db.query(User).filter(User.email == EMAIL).one().is_active = False
        db.commit()
    finally:
        db.close()
    assert login(api).status_code == 403


# --- Protecting the data endpoints -----------------------------------------

@pytest.mark.parametrize(
    "path", ["/api/courses/", "/api/students/", "/api/grades/", "/api/stats/"]
)
def test_data_endpoints_refuse_anonymous_requests(api, path):
    assert api.get(path).status_code == 401


def test_data_endpoints_refuse_a_garbage_or_unsigned_token(api):
    forged = {"Authorization": "Bearer not.a.token"}
    assert api.get("/api/courses/", headers=forged).status_code == 401


def test_an_access_token_opens_the_data_endpoints(api):
    register(api)
    token = login(api).json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    assert api.get("/api/courses/", headers=headers).status_code == 200
    assert api.get("/api/auth/me", headers=headers).json()["email"] == EMAIL


def test_a_refresh_token_is_not_accepted_as_a_bearer_token(api):
    """
    The two token types share a signing key, so only the "typ" claim keeps the
    long-lived cookie from being replayed against the data endpoints.
    """
    register(api)
    login(api)
    refresh_cookie = api.cookies[config.REFRESH_COOKIE_NAME]
    response = api.get("/api/courses/", headers={"Authorization": f"Bearer {refresh_cookie}"})
    assert response.status_code == 401


def test_deactivating_an_account_invalidates_its_live_access_token(api):
    """The user row is re-read per request rather than trusted from the token."""
    register(api)
    token = login(api).json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    assert api.get("/api/courses/", headers=headers).status_code == 200

    db = TestingSessionLocal()
    try:
        db.query(User).filter(User.email == EMAIL).one().is_active = False
        db.commit()
    finally:
        db.close()

    assert api.get("/api/courses/", headers=headers).status_code == 401


# --- Refresh rotation -------------------------------------------------------

def test_refresh_issues_a_new_pair_and_rotates_the_cookie(api):
    register(api)
    first_access = login(api).json()["access_token"]
    first_cookie = api.cookies[config.REFRESH_COOKIE_NAME]

    response = api.post("/api/auth/refresh")
    assert response.status_code == 200
    assert response.json()["access_token"] != first_access
    assert api.cookies[config.REFRESH_COOKIE_NAME] != first_cookie


def test_refresh_without_a_cookie_is_refused(api):
    assert api.post("/api/auth/refresh").status_code == 401


def test_a_rotated_refresh_token_cannot_be_used_again(api):
    register(api)
    login(api)
    used = api.cookies[config.REFRESH_COOKIE_NAME]
    api.post("/api/auth/refresh")

    replay = api.post("/api/auth/refresh", cookies={config.REFRESH_COOKIE_NAME: used})
    assert replay.status_code == 401


def test_replaying_a_rotated_token_drops_every_session_for_that_account(api):
    """
    Two parties holding the same refresh token means one of them stole it, and
    there is no way to tell which. Both are signed out.
    """
    register(api)
    login(api)
    stolen = api.cookies[config.REFRESH_COOKIE_NAME]
    api.post("/api/auth/refresh")
    current = api.cookies[config.REFRESH_COOKIE_NAME]

    assert api.post("/api/auth/refresh", cookies={config.REFRESH_COOKIE_NAME: stolen}).status_code == 401
    assert api.post("/api/auth/refresh", cookies={config.REFRESH_COOKIE_NAME: current}).status_code == 401


def test_a_refresh_token_for_an_unknown_issuance_is_refused(api):
    """A correctly signed token with no matching row was never issued by us."""
    register(api)
    token, _jti, _expires = create_refresh_token(999)
    assert api.post("/api/auth/refresh", cookies={config.REFRESH_COOKIE_NAME: token}).status_code == 401


def test_logout_revokes_the_session_and_clears_the_cookie(api):
    register(api)
    login(api)
    revoked = api.cookies[config.REFRESH_COOKIE_NAME]

    response = api.post("/api/auth/logout")
    assert response.status_code == 204

    db = TestingSessionLocal()
    try:
        assert db.query(RefreshToken).filter(RefreshToken.revoked_at.isnot(None)).count() == 1
    finally:
        db.close()

    assert api.post("/api/auth/refresh", cookies={config.REFRESH_COOKIE_NAME: revoked}).status_code == 401


def test_logout_without_a_session_is_not_an_error(api):
    assert api.post("/api/auth/logout").status_code == 204


# --- Token encoding ---------------------------------------------------------

def test_decode_token_rejects_the_wrong_token_type():
    token, _jti, _expires = create_refresh_token(1)
    assert decode_token(token, REFRESH_TOKEN_TYPE)["sub"] == "1"
    with pytest.raises(TokenError):
        decode_token(token, ACCESS_TOKEN_TYPE)


def test_decode_token_rejects_a_token_signed_with_another_key():
    import jwt

    forged = jwt.encode(
        {"sub": "1", "typ": ACCESS_TOKEN_TYPE, "jti": "x", "iss": config.JWT_ISSUER,
         "iat": 0, "exp": 9999999999},
        "a-different-secret",
        algorithm=config.JWT_ALGORITHM,
    )
    with pytest.raises(TokenError):
        decode_token(forged, ACCESS_TOKEN_TYPE)
