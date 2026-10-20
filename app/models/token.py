"""ORM model for authentication tokens."""

import uuid

from tortoise import fields
from tortoise.models import Model


class Token(Model):
    """
    Stores JWT tokens issued to authenticated users.

    The ``expired_at`` field is set explicitly on logout (Phase 2).
    A null value means the token is still active.
    """

    token_id = fields.UUIDField(primary_key=True, default=uuid.uuid4)
    user: fields.ForeignKeyRelation = fields.ForeignKeyField(
        "models.User",
        related_name="tokens",
        on_delete=fields.CASCADE,
    )
    token = fields.CharField(max_length=512, unique=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    expired_at = fields.DatetimeField(null=True)

    class Meta:
        table = "tokens"

    def __str__(self) -> str:
        return f"Token(token_id={self.token_id})"
