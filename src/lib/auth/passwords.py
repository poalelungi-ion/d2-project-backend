"""
Password Hashing.

bcrypt only: it is deliberately slow, and every hash carries a random 16-byte
salt inside the string it returns, so two accounts sharing a password still
store different digests. 
"""
import bcrypt

from src.database import config


def hash_password(password: str) -> str:
    """
    Returns a bcrypt hash (salt included) for storage in users.password_hash.

    Raises ValueError for input past bcrypt's 72-byte ceiling rather than
    hashing a silent truncation -- the DTO rejects those before they get here.
    """
    encoded = password.encode("utf-8")
    if len(encoded) > config.MAX_PASSWORD_BYTES:
        raise ValueError(f"Password exceeds {config.MAX_PASSWORD_BYTES} bytes")
    return bcrypt.hashpw(encoded, bcrypt.gensalt(rounds=config.BCRYPT_ROUNDS)).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    """
    Constant-time comparison of a candidate password against a stored hash.
    """
    try:
        return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))
    except (ValueError, TypeError):
        return False
