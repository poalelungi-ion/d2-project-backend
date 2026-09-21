"""
Reset an account's password from the command line.

Passwords are stored as bcrypt hashes and cannot be read back, so a forgotten
one has to be replaced rather than recovered. There is no self-service reset in
the application, which makes this the supported way to get someone back in.

    python scripts/set_password.py bashyal@uni-hildesheim.de

The new password is read from a hidden prompt rather than an argument, so it
does not land in the shell history or in the process list. Run it with the same
DATABASE_URL the server uses:

    DATABASE_URL="postgresql://spa_user:spa_password@localhost/spa_db" \
      python scripts/set_password.py <email>

Every existing session for the account is revoked, on the assumption that a
password is being changed because the old one may be in the wrong hands.
"""
import argparse
from datetime import datetime, timezone
from getpass import getpass
from pathlib import Path
import sys

# Run from anywhere: this file lives one level below the package root, which is
# what "src." resolves against. migrations/env.py does the same.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.database import config  # noqa: E402
from src.database.connection import SessionLocal  # noqa: E402
from src.database.models import RefreshToken, User  # noqa: E402
from src.lib.auth.passwords import hash_password  # noqa: E402


def read_new_password() -> str:
    """Prompts twice and enforces the same length rules as registration."""
    password = getpass("New password: ")
    if password != getpass("Repeat password: "):
        sys.exit("Passwords do not match.")

    if len(password) < config.MIN_PASSWORD_LENGTH:
        sys.exit(f"Password must be at least {config.MIN_PASSWORD_LENGTH} characters.")
    if len(password.encode("utf-8")) > config.MAX_PASSWORD_BYTES:
        sys.exit(f"Password must be at most {config.MAX_PASSWORD_BYTES} bytes.")
    return password


def main() -> None:
    parser = argparse.ArgumentParser(description="Set an account's password.")
    parser.add_argument("email", help="Address of the account to update")
    parser.add_argument(
        "--list",
        action="store_true",
        help="List the registered addresses and exit, without changing anything",
    )
    args = parser.parse_args()

    db = SessionLocal()
    try:
        if args.list:
            for user in db.query(User).order_by(User.user_id).all():
                state = "active" if user.is_active else "disabled"
                print(f"{user.user_id}\t{user.email}\t{user.name}\t{state}")
            return

        # Matched the way login matches, so "Bashyal@..." finds the same row.
        email = args.email.strip().lower()
        user = db.query(User).filter(User.email == email).first()
        if user is None:
            known = ", ".join(u.email for u in db.query(User).all()) or "none"
            sys.exit(f"No account for {email}. Registered addresses: {known}")

        user.password_hash = hash_password(read_new_password())

        revoked = (
            db.query(RefreshToken)
            .filter(RefreshToken.user_id == user.user_id, RefreshToken.revoked_at.is_(None))
            .update({RefreshToken.revoked_at: datetime.now(timezone.utc)}, synchronize_session=False)
        )
        db.commit()

        print(f"Password updated for {user.email}. Sessions revoked: {revoked}.")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
