"""ORM model for menu items."""

from tortoise import fields
from tortoise.models import Model


class MenuItem(Model):
    """
    Represents a dish or beverage available in a restaurant's menu.

    ``quantity`` tracks available stock; it must stay >= 0 at the
    application layer when orders are placed (Phase 4).
    """

    id = fields.IntField(primary_key=True, generated=True)
    restaurant: fields.ForeignKeyRelation = fields.ForeignKeyField(
        "models.Restaurant",
        related_name="menu_items",
        on_delete=fields.CASCADE,
    )
    name = fields.CharField(max_length=255)
    description = fields.CharField(max_length=500, null=True)
    price = fields.DecimalField(max_digits=10, decimal_places=2)
    quantity = fields.IntField(default=0)

    class Meta:
        table = "menu_items"

    def __str__(self) -> str:
        return f"MenuItem(id={self.id}, name={self.name}, price={self.price})"
