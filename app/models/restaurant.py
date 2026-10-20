"""ORM models for Restaurant and RestaurantOwner."""

from tortoise import fields
from tortoise.models import Model


class Restaurant(Model):
    """
    Represents a restaurant in the platform.

    ``owner`` stores the primary owner (admin-assigned in Phase 3).
    Additional co-owners are tracked via the ``RestaurantOwner`` join table.
    """

    restaurant_id = fields.IntField(primary_key=True, generated=True)
    owner: fields.ForeignKeyRelation = fields.ForeignKeyField(
        "models.User",
        related_name="owned_restaurants",
        on_delete=fields.CASCADE,
    )
    name = fields.CharField(max_length=255)
    description = fields.TextField(null=True)
    city = fields.CharField(max_length=100)
    state = fields.CharField(max_length=100)
    zip_code = fields.CharField(max_length=20)
    is_active = fields.BooleanField(default=True)
    rating = fields.DecimalField(max_digits=3, decimal_places=1, null=True)

    class Meta:
        table = "restaurants"

    def __str__(self) -> str:
        return f"Restaurant(id={self.restaurant_id}, name={self.name})"


class RestaurantOwner(Model):
    """
    Many-to-many join table tracking which users own which restaurants.

    Allows a restaurant to have multiple owners and a user to own
    multiple restaurants.
    """

    id = fields.IntField(primary_key=True, generated=True)
    restaurant: fields.ForeignKeyRelation[Restaurant] = fields.ForeignKeyField(
        "models.Restaurant",
        related_name="restaurant_owners",
        on_delete=fields.CASCADE,
    )
    user: fields.ForeignKeyRelation = fields.ForeignKeyField(
        "models.User",
        related_name="restaurant_ownerships",
        on_delete=fields.CASCADE,
    )

    class Meta:
        table = "restaurant_owners"
        unique_together = [("restaurant", "user")]

    def __str__(self) -> str:
        return (
            f"RestaurantOwner("
            f"restaurant_id={self.restaurant_id}, user_id={self.user_id})"
        )
