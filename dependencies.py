"""
Shared FastAPI dependencies.

This module exists so that authentication is defined once. It previously
appeared as an identical copy in main.py and in all five router modules,
which meant a change to the scheme had to be made in six places.
"""
from fastapi import Header, HTTPException

import config


def verify_token(authorization: str = Header(None)):
    """
    Rejects any request whose Authorization header does not carry the
    configured bearer token. Attach it to mutating endpoints with
    dependencies=[Depends(verify_token)].
    """
    if authorization != f"Bearer {config.API_TOKEN}":
        raise HTTPException(status_code=401, detail="Unauthorized")
    return True
