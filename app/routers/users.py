"""API router for User CRUD operations."""

from typing import Any
from uuid import UUID

from fastapi import APIRouter, status
from tortoise.exceptions import DoesNotExist, IntegrityError

from app.constants import MSG_EMAIL_ALREADY_EXISTS, MSG_USER_NOT_FOUND
from app.models.user import Address, User
from app.schemas.common import SuccessResponse
from app.schemas.user import UserCreate, UserResponse, UserUpdate
from app.utils.helpers import hash_password, http_error

router = APIRouter(prefix="/users", tags=["Users"])


# ── Private Helpers ───────────────────────────────────────────────────────────


async def _build_user_response(user: User) -> UserResponse:
    """
    Construct a ``UserResponse`` from a ``User`` ORM instance.

    Fetches the related ``Address`` record to flatten the address fields
    (city, state, zipcode) into the response object.

    Args:
        user: Tortoise ``User`` model instance.

    Returns:
        Populated ``UserResponse`` Pydantic schema.
    """
    address = await Address.get_or_none(user=user)
    return UserResponse(
        id=str(user.user_id),
        email=user.email,
        name=user.name,
        city=address.city if address else "",
        state=address.state if address else "",
        zipcode=address.zip_code if address else "",
        balance=user.balance,
        is_admin=user.is_admin,
    )


# ── Endpoints ─────────────────────────────────────────────────────────────────


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=SuccessResponse[UserResponse],
    summary="Create a new user",
    responses={
        201: {"description": "User created successfully."},
        400: {"description": "Email already registered or invalid data."},
    },
)
async def create_user(payload: UserCreate) -> Any:
    """
    Register a new user and their address.

    - Checks for duplicate email before insertion.
    - Stores the password as a bcrypt hash — never in plain text.
    - Returns **201** on success with the new user's details.
    - Returns **400** if the email is already taken.
    """
    if await User.filter(email=payload.email, is_deleted=False).exists():
        http_error(status.HTTP_400_BAD_REQUEST, MSG_EMAIL_ALREADY_EXISTS)

    try:
        user = await User.create(
            email=payload.email,
            name=payload.name,
            password_hash=hash_password(payload.password),
            balance=payload.balance,
        )
        await Address.create(
            user=user,
            city=payload.city,
            state=payload.state,
            zip_code=payload.zipcode,
        )
    except IntegrityError:
        # Race condition: another request inserted the same email between
        # our exists() check and the INSERT.
        http_error(status.HTTP_400_BAD_REQUEST, MSG_EMAIL_ALREADY_EXISTS)

    user_data = await _build_user_response(user)
    return SuccessResponse[UserResponse](data=user_data)


@router.get(
    "/{user_id}/",
    status_code=status.HTTP_200_OK,
    response_model=SuccessResponse[UserResponse],
    summary="Get a user by ID",
    responses={
        200: {"description": "User retrieved successfully."},
        404: {"description": "User with given ID does not exist."},
    },
)
async def get_user(user_id: UUID) -> Any:
    """
    Retrieve details of a specific user by their UUID.

    - Returns **200** with the user's details on success.
    - Returns **404** if no active user with ``user_id`` exists
      (includes soft-deleted users).
    """
    try:
        user = await User.get(user_id=user_id, is_deleted=False)
    except DoesNotExist:
        http_error(status.HTTP_404_NOT_FOUND, MSG_USER_NOT_FOUND)

    user_data = await _build_user_response(user)
    return SuccessResponse[UserResponse](data=user_data)


@router.put(
    "/{user_id}/",
    status_code=status.HTTP_200_OK,
    response_model=SuccessResponse[UserResponse],
    summary="Update a user by ID",
    responses={
        200: {"description": "User updated successfully."},
        400: {"description": "Duplicate email or invalid data."},
        404: {"description": "User with given ID does not exist."},
    },
)
async def update_user(user_id: UUID, payload: UserUpdate) -> Any:
    """
    Update one or more fields of an existing user.

    Only fields present in the request body are modified; omitted fields
    remain unchanged.

    - Returns **200** with the updated user details on success.
    - Returns **400** if the new email is already registered to another user.
    - Returns **404** if the user does not exist.
    """
    try:
        user = await User.get(user_id=user_id, is_deleted=False)
    except DoesNotExist:
        http_error(status.HTTP_404_NOT_FOUND, MSG_USER_NOT_FOUND)

    # Guard against email collision before making any changes
    if payload.email is not None and payload.email != user.email:
        if await User.filter(email=payload.email, is_deleted=False).exists():
            http_error(status.HTTP_400_BAD_REQUEST, MSG_EMAIL_ALREADY_EXISTS)

    # ── Update user-level fields ──────────────────────────────────────────────
    user_fields: list[str] = []

    if payload.email is not None:
        user.email = payload.email
        user_fields.append("email")

    if payload.name is not None:
        user.name = payload.name
        user_fields.append("name")

    if payload.password is not None:
        user.password_hash = hash_password(payload.password)
        user_fields.append("password_hash")

    if payload.balance is not None:
        user.balance = payload.balance
        user_fields.append("balance")

    if user_fields:
        await user.save(update_fields=user_fields)

    # ── Update address fields (if any were supplied) ──────────────────────────
    if any(v is not None for v in [payload.city, payload.state, payload.zipcode]):
        address = await Address.get_or_none(user=user)
        if address is None:
            # Create address if it somehow doesn't exist yet
            await Address.create(
                user=user,
                city=payload.city or "",
                state=payload.state or "",
                zip_code=payload.zipcode or "",
            )
        else:
            addr_fields: list[str] = []
            if payload.city is not None:
                address.city = payload.city
                addr_fields.append("city")
            if payload.state is not None:
                address.state = payload.state
                addr_fields.append("state")
            if payload.zipcode is not None:
                address.zip_code = payload.zipcode
                addr_fields.append("zip_code")
            if addr_fields:
                await address.save(update_fields=addr_fields)

    user_data = await _build_user_response(user)
    return SuccessResponse[UserResponse](data=user_data)


@router.delete(
    "/{user_id}/",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Soft-delete a user by ID",
    responses={
        204: {"description": "User deleted successfully (soft delete)."},
        404: {"description": "User with given ID does not exist."},
    },
)
async def delete_user(user_id: UUID) -> None:
    """
    Soft-delete a user by setting ``is_deleted = True``.

    The database record is **not** physically removed; the user simply
    becomes invisible to all other API endpoints.

    - Returns **204** with no body on success.
    - Returns **404** if the user does not exist.
    """
    try:
        user = await User.get(user_id=user_id, is_deleted=False)
    except DoesNotExist:
        http_error(status.HTTP_404_NOT_FOUND, MSG_USER_NOT_FOUND)

    user.is_deleted = True
    await user.save(update_fields=["is_deleted"])
