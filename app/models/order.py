"""ORM models for orders and order items."""

import uuid

from tortoise import fields
from tortoise.models import Model


class Order(Model):
    """
    Represents a customer's order placed at a restaurant.

    All items in a single order must belong to the same restaurant
    (enforced at the application layer in Phase 4).
    """

    order_id = fields.UUIDField(primary_key=True, default=uuid.uuid4)
    user: fields.ForeignKeyRelation = fields.ForeignKeyField(
        "models.User",
        related_name="orders",
        on_delete=fields.CASCADE,
    )
    restaurant: fields.ForeignKeyRelation = fields.ForeignKeyField(
        "models.Restaurant",
        related_name="orders",
        on_delete=fields.CASCADE,
    )
    city = fields.CharField(max_length=100, null=True)
    state = fields.CharField(max_length=100, null=True)
    zip_code = fields.CharField(max_length=20, null=True)
    total_price = fields.FloatField()
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "orders"

    def __str__(self) -> str:
        return f"Order(order_id={self.order_id}, total_price={self.total_price})"


class OrderItem(Model):
    """
    Represents one line item within an Order.

    ``price`` is snapshot of the menu item price at the time of order,
    so historical order totals remain accurate even if prices change later.
    """

    order_item_id = fields.UUIDField(primary_key=True, default=uuid.uuid4)
    order: fields.ForeignKeyRelation[Order] = fields.ForeignKeyField(
        "models.Order",
        related_name="order_items",
        on_delete=fields.CASCADE,
    )
    menu_item: fields.ForeignKeyRelation = fields.ForeignKeyField(
        "models.MenuItem",
        related_name="order_items",
        on_delete=fields.CASCADE,
    )
    quantity = fields.IntField()
    price = fields.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        table = "order_items"

    def __str__(self) -> str:
        return (
            f"OrderItem(id={self.order_item_id}, quantity={self.quantity})"
        )
