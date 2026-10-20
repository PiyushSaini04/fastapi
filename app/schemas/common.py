"""
Shared Pydantic response schemas used across the entire application.

All endpoints return either a ``SuccessResponse`` or raise an
``HTTPException`` whose detail is formatted as an ``ErrorResponse``-shaped
dict.  This guarantees a consistent JSON envelope for every API response.
"""

from typing import Generic, Optional, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class SuccessResponse(BaseModel, Generic[T]):
    """
    Standard success envelope.

    Example::

        {
            "status": "success",
            "data": { ... }
        }
    """

    status: str = "success"
    data: T


class ErrorDetail(BaseModel):
    """A single field-level validation or business-logic error."""

    field: Optional[str] = None
    message: str


class ErrorResponse(BaseModel):
    """
    Standard error envelope (for documentation purposes).

    The actual error body is constructed inside ``http_error()`` and
    returned via ``HTTPException.detail``.

    Example::

        {
            "status": "error",
            "message": "User not found.",
            "details": null
        }
    """

    status: str = "error"
    message: str
    details: Optional[list[ErrorDetail]] = None
