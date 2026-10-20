"""
FastAPI application entry point.

Startup sequence:
  1. Exception handlers are registered (validation + HTTP).
  2. Routers are included.
  3. Tortoise ORM is wired to the app lifecycle via register_tortoise()
     (skipped when TESTING=true so pytest manages the DB directly).
"""

import os

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from tortoise.contrib.fastapi import register_tortoise

from app.database import TORTOISE_ORM
from app.routers import users

# ── Application Instance ──────────────────────────────────────────────────────

app = FastAPI(
    title="Restaurant Management API",
    description=(
        "REST APIs for a basic Restaurant Management Application.\n\n"
        "Phase 1 covers User CRUD with full Pydantic validation, "
        "soft-delete, and Aerich-managed migrations."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── Exception Handlers ────────────────────────────────────────────────────────


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    """
    Convert Pydantic ``RequestValidationError`` to the standard error envelope.

    Extracts per-field error messages so the client can display them
    next to the relevant input field.
    """
    details = [
        {
            "field": " -> ".join(str(loc) for loc in err["loc"]),
            "message": err["msg"],
        }
        for err in exc.errors()
    ]
    return JSONResponse(
        status_code=422,
        content={
            "status": "error",
            "message": "Validation error.",
            "details": details,
        },
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(
    request: Request,
    exc: HTTPException,
) -> JSONResponse:
    """
    Serialise all ``HTTPException`` instances using the standard error envelope.

    When ``exc.detail`` is already a dict (raised via ``http_error()``),
    it is passed through as-is.  Plain string details are wrapped.
    """
    if isinstance(exc.detail, dict):
        return JSONResponse(status_code=exc.status_code, content=exc.detail)
    return JSONResponse(
        status_code=exc.status_code,
        content={"status": "error", "message": str(exc.detail)},
    )


# ── Routers ───────────────────────────────────────────────────────────────────

app.include_router(users.router)

# ── Database ──────────────────────────────────────────────────────────────────

# When TESTING is set, pytest (conftest.py) manages the Tortoise lifecycle
# directly with an in-memory SQLite database, so we must not register the
# production startup/shutdown hooks here.
if not os.getenv("TESTING"):
    register_tortoise(
        app,
        config=TORTOISE_ORM,
        generate_schemas=False,   # Managed exclusively by Aerich migrations.
        add_exception_handlers=True,
    )
