"""Pydantic schemas for User-related API requests and responses."""

import re
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.constants import (
    MAX_CITY_LEN,
    MAX_NAME_LEN,
    MAX_PASSWORD_LEN,
    MAX_STATE_LEN,
    MIN_CITY_LEN,
    MIN_NAME_LEN,
    MIN_PASSWORD_LEN,
    MIN_STATE_LEN,
    ZIP_CODE_PATTERN,
)

_ZIP_REGEX: re.Pattern[str] = re.compile(ZIP_CODE_PATTERN)


class UserCreate(BaseModel):
    """
    Input schema for creating a new user.

    Validates:
    - ``email``    — valid RFC-5321 address (Pydantic EmailStr)
    - ``name``     — 1–255 chars, not blank/whitespace-only
    - ``password`` — 8–128 chars
    - ``city``     — 2–100 chars
    - ``state``    — 2–100 chars
    - ``zipcode``  — US format XXXXX or XXXXX-XXXX
    - ``balance``  — decimal >= 0
    """

    email: EmailStr
    name: str = Field(min_length=MIN_NAME_LEN, max_length=MAX_NAME_LEN)
    password: str = Field(min_length=MIN_PASSWORD_LEN, max_length=MAX_PASSWORD_LEN)
    city: str = Field(min_length=MIN_CITY_LEN, max_length=MAX_CITY_LEN)
    state: str = Field(min_length=MIN_STATE_LEN, max_length=MAX_STATE_LEN)
    zipcode: str
    balance: Decimal = Field(default=Decimal("0.00"), ge=0)

    @field_validator("zipcode")
    @classmethod
    def validate_zipcode(cls, value: str) -> str:
        """Enforce US ZIP code format (XXXXX or XXXXX-XXXX)."""
        stripped = value.strip()
        if not _ZIP_REGEX.match(stripped):
            raise ValueError(
                "Zip code must be in the format XXXXX or XXXXX-XXXX."
            )
        return stripped

    @field_validator("name", "city", "state", mode="before")
    @classmethod
    def strip_and_reject_blank(cls, value: object) -> object:
        """Strip whitespace and reject fields that are blank after stripping."""
        if isinstance(value, str):
            stripped = value.strip()
            if not stripped:
                raise ValueError("This field must not be blank or whitespace-only.")
            return stripped
        return value


class UserUpdate(BaseModel):
    """
    Input schema for updating an existing user.

    All fields are optional — only supplied fields are updated.
    The same validation rules as ``UserCreate`` apply to any field provided.
    """

    email: Optional[EmailStr] = None
    name: Optional[str] = Field(None, min_length=MIN_NAME_LEN, max_length=MAX_NAME_LEN)
    password: Optional[str] = Field(
        None, min_length=MIN_PASSWORD_LEN, max_length=MAX_PASSWORD_LEN
    )
    city: Optional[str] = Field(None, min_length=MIN_CITY_LEN, max_length=MAX_CITY_LEN)
    state: Optional[str] = Field(
        None, min_length=MIN_STATE_LEN, max_length=MAX_STATE_LEN
    )
    zipcode: Optional[str] = None
    balance: Optional[Decimal] = Field(None, ge=0)

    @field_validator("zipcode")
    @classmethod
    def validate_zipcode(cls, value: Optional[str]) -> Optional[str]:
        """Enforce US ZIP code format if a value is provided."""
        if value is not None:
            stripped = value.strip()
            if not _ZIP_REGEX.match(stripped):
                raise ValueError(
                    "Zip code must be in the format XXXXX or XXXXX-XXXX."
                )
            return stripped
        return value

    @field_validator("name", "city", "state", mode="before")
    @classmethod
    def strip_whitespace(cls, value: object) -> object:
        """Strip surrounding whitespace from string fields if provided."""
        if isinstance(value, str):
            return value.strip()
        return value


class UserResponse(BaseModel):
    """
    Output schema representing a user resource in API responses.

    ``password_hash`` is intentionally excluded.
    Address fields (city, state, zipcode) are flattened from the
    related ``Address`` model for a simpler API surface.
    """

    id: str
    email: str
    name: str
    city: str
    state: str
    zipcode: str
    balance: Decimal
    is_admin: bool
