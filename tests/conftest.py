"""
Pytest configuration and shared fixtures.

IMPORTANT: ``TESTING`` is set at module level *before* any application
modules are imported.  This prevents ``main.py`` from calling
``register_tortoise()`` with the production database config.
Each test function gets its own isolated in-memory SQLite database via
the ``client`` fixture so tests never interfere with each other.
"""

import os

# Must be set BEFORE importing anything from the ``app`` package so that
# the conditional ``if not os.getenv("TESTING"):`` in main.py fires correctly.
os.environ["TESTING"] = "true"

import pytest_asyncio  # noqa: E402
from httpx import ASGITransport, AsyncClient  # noqa: E402
from tortoise import Tortoise  # noqa: E402

from app.main import app  # noqa: E402

# ── Test Database Configuration ───────────────────────────────────────────────

_TEST_MODELS: list[str] = [
    "app.models.user",
    "app.models.token",
    "app.models.restaurant",
    "app.models.menu",
    "app.models.order",
]

_TEST_TORTOISE_CONFIG: dict = {
    "connections": {"default": "sqlite://:memory:"},
    "apps": {
        "models": {
            "models": _TEST_MODELS,
            "default_connection": "default",
        }
    },
}

# ── Fixtures ──────────────────────────────────────────────────────────────────


@pytest_asyncio.fixture(scope="function")
async def client() -> AsyncClient:
    """
    Provide an ``AsyncClient`` backed by a fresh in-memory SQLite database.

    Lifecycle per test function:
      1. Initialise Tortoise with in-memory SQLite.
      2. Auto-generate all table schemas.
      3. Yield the HTTP client for the test to use.
      4. Close all database connections (in-memory DB is discarded).
    """
    await Tortoise.init(config=_TEST_TORTOISE_CONFIG)
    await Tortoise.generate_schemas()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    await Tortoise.close_connections()
