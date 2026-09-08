"""Backward-compatible shim for dependencies."""
from src.lib.auth.validator import verify_token
__all__ = ["verify_token"]
