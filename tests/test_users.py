"""
Test suite for the User CRUD API endpoints.

Covers:
  - POST /users/   — create (success + all validation failures)
  - GET  /users/{id}/ — retrieve (success + 404)
  - PUT  /users/{id}/ — update  (success + 400 + 404 + 422)
  - DELETE /users/{id}/ — soft-delete (204 + 404 + post-delete 404)
"""

from typing import Any

import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio

# ── Shared Test Data ──────────────────────────────────────────────────────────

_VALID_USER: dict[str, Any] = {
    "email": "john.doe@example.com",
    "name": "John Doe",
    "password": "securepassword123",
    "city": "New York",
    "state": "NY",
    "zipcode": "10001",
    "balance": "100.00",
}


# ── Helpers ───────────────────────────────────────────────────────────────────


async def _create_user(
    client: AsyncClient,
    overrides: dict[str, Any] | None = None,
):
    """POST /users/ with optional field overrides and return the response."""
    payload = {**_VALID_USER, **(overrides or {})}
    return await client.post("/users/", json=payload)


# ── POST /users/ ─────────────────────────────────────────────────────────────


class TestCreateUser:
    async def test_success_returns_201(self, client: AsyncClient) -> None:
        """A fully valid payload should create a user and return 201."""
        response = await _create_user(client)

        assert response.status_code == 201
        body = response.json()
        assert body["status"] == "success"
        assert body["data"]["email"] == _VALID_USER["email"]
        assert body["data"]["name"] == _VALID_USER["name"]
        assert body["data"]["city"] == _VALID_USER["city"]
        assert body["data"]["state"] == _VALID_USER["state"]
        assert body["data"]["zipcode"] == _VALID_USER["zipcode"]
        assert "id" in body["data"]

    async def test_duplicate_email_returns_400(self, client: AsyncClient) -> None:
        """Registering the same email twice should return 400."""
        await _create_user(client)
        response = await _create_user(client)

        assert response.status_code == 400
        assert response.json()["status"] == "error"

    async def test_invalid_email_returns_422(self, client: AsyncClient) -> None:
        """A malformed email string should fail Pydantic validation (422)."""
        response = await _create_user(client, {"email": "not-an-email"})
        assert response.status_code == 422

    async def test_negative_balance_returns_422(self, client: AsyncClient) -> None:
        """A negative balance should be rejected by the ``ge=0`` constraint."""
        response = await _create_user(client, {"balance": "-50.00"})
        assert response.status_code == 422

    async def test_short_password_returns_422(self, client: AsyncClient) -> None:
        """A password below the minimum length should return 422."""
        response = await _create_user(client, {"password": "short"})
        assert response.status_code == 422

    async def test_invalid_zipcode_returns_422(self, client: AsyncClient) -> None:
        """An alphanumeric zip code should fail the regex validator."""
        response = await _create_user(client, {"zipcode": "ABCDE"})
        assert response.status_code == 422

    async def test_blank_name_returns_422(self, client: AsyncClient) -> None:
        """A whitespace-only name should be caught by the strip_and_reject_blank validator."""
        response = await _create_user(client, {"name": "   "})
        assert response.status_code == 422

    async def test_extended_zipcode_format_accepted(self, client: AsyncClient) -> None:
        """ZIP+4 format (XXXXX-XXXX) should be accepted."""
        response = await _create_user(client, {"zipcode": "10001-1234"})
        assert response.status_code == 201


# ── GET /users/{user_id}/ ─────────────────────────────────────────────────────


class TestGetUser:
    async def test_success_returns_200(self, client: AsyncClient) -> None:
        """Fetching a known user should return 200 and full user details."""
        create_resp = await _create_user(client)
        user_id = create_resp.json()["data"]["id"]

        response = await client.get(f"/users/{user_id}/")

        assert response.status_code == 200
        body = response.json()
        assert body["status"] == "success"
        assert body["data"]["email"] == _VALID_USER["email"]

    async def test_not_found_returns_404(self, client: AsyncClient) -> None:
        """Requesting a non-existent UUID should return 404."""
        response = await client.get("/users/00000000-0000-0000-0000-000000000000/")

        assert response.status_code == 404
        assert response.json()["status"] == "error"


# ── PUT /users/{user_id}/ ─────────────────────────────────────────────────────


class TestUpdateUser:
    async def test_success_updates_name_and_city(self, client: AsyncClient) -> None:
        """Partial update of name and city should reflect in the 200 response."""
        create_resp = await _create_user(client)
        user_id = create_resp.json()["data"]["id"]

        response = await client.put(
            f"/users/{user_id}/",
            json={"name": "Jane Doe", "city": "Los Angeles"},
        )

        assert response.status_code == 200
        data = response.json()["data"]
        assert data["name"] == "Jane Doe"
        assert data["city"] == "Los Angeles"
        # Unchanged fields should be preserved
        assert data["email"] == _VALID_USER["email"]

    async def test_duplicate_email_returns_400(self, client: AsyncClient) -> None:
        """Attempting to steal another user's email should return 400."""
        await _create_user(client, {"email": "user1@example.com"})
        create_resp = await _create_user(client, {"email": "user2@example.com"})
        user_id = create_resp.json()["data"]["id"]

        response = await client.put(
            f"/users/{user_id}/",
            json={"email": "user1@example.com"},
        )

        assert response.status_code == 400

    async def test_same_email_update_accepted(self, client: AsyncClient) -> None:
        """Updating a user's email to their own current email should succeed."""
        create_resp = await _create_user(client)
        user_id = create_resp.json()["data"]["id"]

        response = await client.put(
            f"/users/{user_id}/",
            json={"email": _VALID_USER["email"]},
        )

        assert response.status_code == 200

    async def test_not_found_returns_404(self, client: AsyncClient) -> None:
        """Updating a non-existent user should return 404."""
        response = await client.put(
            "/users/00000000-0000-0000-0000-000000000000/",
            json={"name": "Ghost"},
        )

        assert response.status_code == 404

    async def test_negative_balance_returns_422(self, client: AsyncClient) -> None:
        """Setting balance to a negative value should fail validation (422)."""
        create_resp = await _create_user(client)
        user_id = create_resp.json()["data"]["id"]

        response = await client.put(f"/users/{user_id}/", json={"balance": "-10"})

        assert response.status_code == 422


# ── DELETE /users/{user_id}/ ──────────────────────────────────────────────────


class TestDeleteUser:
    async def test_success_returns_204(self, client: AsyncClient) -> None:
        """Deleting an existing user should return 204 with no body."""
        create_resp = await _create_user(client)
        user_id = create_resp.json()["data"]["id"]

        response = await client.delete(f"/users/{user_id}/")

        assert response.status_code == 204
        assert response.content == b""

    async def test_not_found_returns_404(self, client: AsyncClient) -> None:
        """Deleting a non-existent user should return 404."""
        response = await client.delete(
            "/users/00000000-0000-0000-0000-000000000000/"
        )

        assert response.status_code == 404

    async def test_get_after_delete_returns_404(self, client: AsyncClient) -> None:
        """After a soft-delete, GET on that user should return 404."""
        create_resp = await _create_user(client)
        user_id = create_resp.json()["data"]["id"]

        await client.delete(f"/users/{user_id}/")
        response = await client.get(f"/users/{user_id}/")

        assert response.status_code == 404

    async def test_soft_delete_preserves_db_record(self, client: AsyncClient) -> None:
        """Soft-deleted user's record must remain in the DB with is_deleted=True."""
        from app.models.user import User

        create_resp = await _create_user(client)
        user_id = create_resp.json()["data"]["id"]

        await client.delete(f"/users/{user_id}/")

        # Bypass the is_deleted filter to confirm the row still exists
        user = await User.get(user_id=user_id)
        assert user.is_deleted is True
