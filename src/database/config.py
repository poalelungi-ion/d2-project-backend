"""
Application configuration module.
Reads environment variables for database connection, authentication, and CORS.
"""
import os

DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://spa_user:spa_password@db/spa_db"
)

# --- Account policy ---------------------------------------------------------

# Only addresses inside the university's mail domain may hold an account. This
# is the single source of truth for the rule: the registration DTO validates
# against it and the client mirrors it purely to give instant form feedback
# (src/utils/constants.ts). Kept configurable so a test or a second faculty
# deployment does not need a code change.
UNIVERSITY_EMAIL_DOMAIN = os.getenv("UNIVERSITY_EMAIL_DOMAIN", "uni-hildesheim.de").lower().lstrip("@")

# bcrypt hashes at most 72 bytes of input and silently ignores the rest, so a
# longer password would make every suffix equivalent. Registration rejects them
# instead of truncating.
MAX_PASSWORD_BYTES = 72
MIN_PASSWORD_LENGTH = int(os.getenv("MIN_PASSWORD_LENGTH", "10"))

# Work factor for bcrypt. Each increment doubles the hashing cost.
BCRYPT_ROUNDS = int(os.getenv("BCRYPT_ROUNDS", "12"))

# --- Tokens -----------------------------------------------------------------

# Signing key for both token types. The development fallback is deliberately
# recognisable: app startup refuses to run with it once DEBUG is off.
DEV_JWT_SECRET = "insecure-development-secret-change-me"
JWT_SECRET = os.getenv("JWT_SECRET", DEV_JWT_SECRET)
JWT_ALGORITHM = "HS256"
JWT_ISSUER = "spa-backend"

# Short-lived, held only in the client's memory and replayed on every request.
ACCESS_TOKEN_TTL_MINUTES = int(os.getenv("ACCESS_TOKEN_TTL_MINUTES", "15"))
# Long-lived, delivered as an httpOnly cookie and rotated on every use.
REFRESH_TOKEN_TTL_DAYS = int(os.getenv("REFRESH_TOKEN_TTL_DAYS", "14"))

REFRESH_COOKIE_NAME = "spa_refresh_token"
# Scoping the cookie to the auth router keeps it off every other request, so
# the only code that can ever see it is the code that rotates it.
REFRESH_COOKIE_PATH = "/api/auth"
# Must be true wherever the site is served over HTTPS; false locally so the
# cookie survives plain-HTTP development.
COOKIE_SECURE = os.getenv("COOKIE_SECURE", "false").lower() == "true"
# "lax" covers client and API sharing a registrable domain (including
# localhost:5173 -> localhost:8000). Set "none" -- which requires
# COOKIE_SECURE=true -- if they are genuinely cross-site.
COOKIE_SAMESITE = os.getenv("COOKIE_SAMESITE", "lax").lower()

# --- Environment ------------------------------------------------------------

DEBUG = os.getenv("DEBUG", "true").lower() == "true"

# Credentialed requests cannot use a wildcard origin: the browser rejects
# "Access-Control-Allow-Origin: *" whenever the request carries cookies, and
# the refresh cookie makes every auth call credentialed. The allow-list is
# therefore explicit, and a "*" left over from the token-based setup is
# dropped with a warning rather than silently breaking login.
DEV_CORS_ORIGINS = ["http://localhost:5173", "http://127.0.0.1:5173"]

_configured_origins = [
    origin.strip()
    for origin in os.getenv("CORS_ORIGINS", ",".join(DEV_CORS_ORIGINS)).split(",")
    if origin.strip()
]
CORS_WILDCARD_REQUESTED = "*" in _configured_origins
CORS_ORIGINS = [o for o in _configured_origins if o != "*"] or DEV_CORS_ORIGINS

SEED_ON_STARTUP = os.getenv("SEED_ON_STARTUP", "true").lower() == "true"

# Optional first account, created on startup when the users table is empty so
# a fresh deployment is reachable without hand-writing a bcrypt hash.
BOOTSTRAP_ADMIN_EMAIL = os.getenv("BOOTSTRAP_ADMIN_EMAIL", "")
BOOTSTRAP_ADMIN_PASSWORD = os.getenv("BOOTSTRAP_ADMIN_PASSWORD", "")
BOOTSTRAP_ADMIN_NAME = os.getenv("BOOTSTRAP_ADMIN_NAME", "Administrator")
