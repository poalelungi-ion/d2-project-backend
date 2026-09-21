"""Backward-compatible shim for dependencies."""
from src.lib.auth.validator import get_current_user, security
__all__ = ["get_current_user", "security"]
