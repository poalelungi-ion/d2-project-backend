"""
Authentication Data Transfer Objects (DTOs).

The university-domain rule lives here, driven by config.UNIVERSITY_EMAIL_DOMAIN,
so a rejected address is a 422 from the schema layer and never reaches a
service. 
"""
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, field_validator

from src.database import config


def normalize_university_email(value: str) -> str:
    """
    Lower-cases the address and enforces the university mail domain.
    """
    email = value.strip().lower()
    domain = email.rsplit("@", 1)[-1]
    if domain != config.UNIVERSITY_EMAIL_DOMAIN:
        raise ValueError(f"Email must be a @{config.UNIVERSITY_EMAIL_DOMAIN} address")
    return email


class RegisterRequest(BaseModel):
    email: EmailStr
    name: str = Field(min_length=1, max_length=120)
    # The upper bound is bcrypt's: it hashes the first 72 bytes and ignores
    # the rest, which would make every longer password interchangeable.
    password: str = Field(min_length=config.MIN_PASSWORD_LENGTH)

    @field_validator("email")
    @classmethod
    def check_domain(cls, value: str) -> str:
        return normalize_university_email(value)

    @field_validator("name")
    @classmethod
    def strip_name(cls, value: str) -> str:
        name = value.strip()
        if not name:
            raise ValueError("Name is required")
        return name

    @field_validator("password")
    @classmethod
    def check_password_length(cls, value: str) -> str:
        if len(value.encode("utf-8")) > config.MAX_PASSWORD_BYTES:
            raise ValueError(f"Password must be at most {config.MAX_PASSWORD_BYTES} bytes")
        return value


class LoginRequest(BaseModel):
    email: EmailStr
    password: str

    @field_validator("email")
    @classmethod
    def lowercase(cls, value: str) -> str:
        # No domain check on login: a wrong domain is simply an unknown account
        return value.strip().lower()


class UserResponse(BaseModel):
    user_id: int
    email: str
    name: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    """
    The login/refresh response body. It deliberately has no refresh token in
    it: that one is set as an httpOnly cookie so no JavaScript on the page,
    including anything injected into it can read or exfiltrate it.
    """
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse
