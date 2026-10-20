"""Shared utility / helper functions used across the application."""

from typing import Any, NoReturn, Optional

import bcrypt
from fastapi import HTTPException


def hash_password(plain_password: str) -> str:
    """
    Hash a plain-text password using bcrypt.

    Args:
        plain_password: The raw password string provided by the user.

    Returns:
        A bcrypt-hashed string safe to store in the database.
    """
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(plain_password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Check whether a plain-text password matches a stored bcrypt hash.

    Args:
        plain_password:  Raw password submitted by the user at login.
        hashed_password: Bcrypt hash retrieved from the database.

    Returns:
        ``True`` if the password is correct, ``False`` otherwise.
    """
    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        hashed_password.encode("utf-8"),
    )


def http_error(
    status_code: int,
    message: str,
    details: Optional[list[dict[str, Any]]] = None,
) -> NoReturn:
    """
    Raise a standardised ``HTTPException`` using the application error envelope.

    The raised exception is caught by the custom ``http_exception_handler``
    registered in ``main.py``, which serialises it as::

        {
            "status": "error",
            "message": "<message>",
            "details": [...]   # omitted when None
        }

    Args:
        status_code: HTTP status code to respond with (e.g. 400, 404).
        message:     Human-readable description of the error.
        details:     Optional list of field-level error dicts.

    Raises:
        HTTPException: Always — this function never returns normally.
    """
    content: dict[str, Any] = {"status": "error", "message": message}
    if details:
        content["details"] = details
    raise HTTPException(status_code=status_code, detail=content)
