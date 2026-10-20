"""
Tortoise ORM configuration dictionary.

This module is the single source of truth for both:
  - The running application  (registered via register_tortoise in main.py)
  - Aerich migration tooling (referenced in pyproject.toml)
"""

from app.config import get_settings

_settings = get_settings()

TORTOISE_ORM: dict = {
    "connections": {
        "default": _settings.DATABASE_URL,
    },
    "apps": {
        "models": {
            "models": [
                # Application models — define ALL models here so that
                # the initial Aerich migration captures the complete schema.
                "app.models.user",
                "app.models.token",
                "app.models.restaurant",
                "app.models.menu",
                "app.models.order",
                # Aerich internal tracking table
                "aerich.models",
            ],
            "default_connection": "default",
        }
    },
}
