"""ORM models for User and Address."""

import uuid

from tortoise import fields
from tortoise.models import Model


class User(Model):
    """
    Represents a registered user in the system.

    A user can be a normal customer (is_admin=False) who places orders,
    or an admin (is_admin=True) who can create restaurants and assign owners.

    Soft-delete is implemented via the ``is_deleted`` flag; deleted users
    are never physically removed from the database.
    """

    user_id = fields.UUIDField(primary_key=True, default=uuid.uuid4)
    name = fields.CharField(max_length=255)
    email = fields.CharField(max_length=255, unique=True)
    password_hash = fields.CharField(max_length=255)
    is_admin = fields.BooleanField(default=False)
    balance = fields.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_deleted = fields.BooleanField(default=False)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "users"

    def __str__(self) -> str:
        return f"User(user_id={self.user_id}, email={self.email})"


class Address(Model):
    """
    Stores the address associated with a user account.

    One-to-one with User (each user has exactly one address record).
    The FK lives on this side to avoid circular dependency at the DB level.
    """

    address_id = fields.IntField(primary_key=True, generated=True)
    user: fields.OneToOneRelation[User] = fields.OneToOneField(
        "models.User",
        related_name="address",
        on_delete=fields.CASCADE,
    )
    city = fields.CharField(max_length=100)
    state = fields.CharField(max_length=100)
    zip_code = fields.CharField(max_length=20)

    class Meta:
        table = "address"

    def __str__(self) -> str:
        return (
            f"Address(address_id={self.address_id}, "
            f"city={self.city}, state={self.state})"
        )
