"""
Forwarder shim for backward compatibility.
Delegates to the modular src.app application.
"""
from src.app import app

__all__ = ["app"]
