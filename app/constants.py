"""Application-wide constants — single source of truth for magic values."""

# ── Field Length Constraints ──────────────────────────────────────────────────

MIN_NAME_LEN: int = 1
MAX_NAME_LEN: int = 255

MIN_CITY_LEN: int = 2
MAX_CITY_LEN: int = 100

MIN_STATE_LEN: int = 2
MAX_STATE_LEN: int = 100

MAX_ZIP_CODE_LEN: int = 20

MIN_PASSWORD_LEN: int = 8
MAX_PASSWORD_LEN: int = 128

# ── Regex Patterns ────────────────────────────────────────────────────────────

# US ZIP code: 12345 or 12345-6789
ZIP_CODE_PATTERN: str = r"^\d{5}(-\d{4})?$"

# ── User-Facing Error Messages ────────────────────────────────────────────────

MSG_USER_NOT_FOUND: str = "User not found."
MSG_EMAIL_ALREADY_EXISTS: str = "A user with this email already exists."
MSG_VALIDATION_ERROR: str = "Validation error."
MSG_INTERNAL_ERROR: str = "An unexpected error occurred. Please try again later."
