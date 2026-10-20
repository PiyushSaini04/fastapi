from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "users" (
    "user_id" CHAR(36) NOT NULL PRIMARY KEY,
    "name" VARCHAR(255) NOT NULL,
    "email" VARCHAR(255) NOT NULL UNIQUE,
    "password_hash" VARCHAR(255) NOT NULL,
    "is_admin" INT NOT NULL,
    "balance" VARCHAR(40) NOT NULL,
    "is_deleted" INT NOT NULL,
    "created_at" TIMESTAMP NOT NULL
) /* Represents a registered user in the system. */;
CREATE TABLE IF NOT EXISTS "address" (
    "address_id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "city" VARCHAR(100) NOT NULL,
    "state" VARCHAR(100) NOT NULL,
    "zip_code" VARCHAR(20) NOT NULL,
    "user_id" CHAR(36) NOT NULL UNIQUE REFERENCES "users" ("user_id") ON DELETE CASCADE
) /* Stores the address associated with a user account. */;
CREATE TABLE IF NOT EXISTS "tokens" (
    "token_id" CHAR(36) NOT NULL PRIMARY KEY,
    "token" VARCHAR(512) NOT NULL UNIQUE,
    "created_at" TIMESTAMP NOT NULL,
    "expired_at" TIMESTAMP,
    "user_id" CHAR(36) NOT NULL REFERENCES "users" ("user_id") ON DELETE CASCADE
) /* Stores JWT tokens issued to authenticated users. */;
CREATE TABLE IF NOT EXISTS "restaurants" (
    "restaurant_id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "name" VARCHAR(255) NOT NULL,
    "description" TEXT,
    "city" VARCHAR(100) NOT NULL,
    "state" VARCHAR(100) NOT NULL,
    "zip_code" VARCHAR(20) NOT NULL,
    "is_active" INT NOT NULL,
    "rating" VARCHAR(40),
    "owner_id" CHAR(36) NOT NULL REFERENCES "users" ("user_id") ON DELETE CASCADE
) /* Represents a restaurant in the platform. */;
CREATE TABLE IF NOT EXISTS "restaurant_owners" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "restaurant_id" INT NOT NULL REFERENCES "restaurants" ("restaurant_id") ON DELETE CASCADE,
    "user_id" CHAR(36) NOT NULL REFERENCES "users" ("user_id") ON DELETE CASCADE,
    CONSTRAINT "uid_restaurant__restaur_72f396" UNIQUE ("restaurant_id", "user_id")
) /* Many-to-many join table tracking which users own which restaurants. */;
CREATE TABLE IF NOT EXISTS "menu_items" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "name" VARCHAR(255) NOT NULL,
    "description" VARCHAR(500),
    "price" VARCHAR(40) NOT NULL,
    "quantity" INT NOT NULL,
    "restaurant_id" INT NOT NULL REFERENCES "restaurants" ("restaurant_id") ON DELETE CASCADE
) /* Represents a dish or beverage available in a restaurant's menu. */;
CREATE TABLE IF NOT EXISTS "orders" (
    "order_id" CHAR(36) NOT NULL PRIMARY KEY,
    "city" VARCHAR(100),
    "state" VARCHAR(100),
    "zip_code" VARCHAR(20),
    "total_price" REAL NOT NULL,
    "created_at" TIMESTAMP NOT NULL,
    "restaurant_id" INT NOT NULL REFERENCES "restaurants" ("restaurant_id") ON DELETE CASCADE,
    "user_id" CHAR(36) NOT NULL REFERENCES "users" ("user_id") ON DELETE CASCADE
) /* Represents a customer's order placed at a restaurant. */;
CREATE TABLE IF NOT EXISTS "order_items" (
    "order_item_id" CHAR(36) NOT NULL PRIMARY KEY,
    "quantity" INT NOT NULL,
    "price" VARCHAR(40) NOT NULL,
    "menu_item_id" INT NOT NULL REFERENCES "menu_items" ("id") ON DELETE CASCADE,
    "order_id" CHAR(36) NOT NULL REFERENCES "orders" ("order_id") ON DELETE CASCADE
) /* Represents one line item within an Order. */;
CREATE TABLE IF NOT EXISTS "aerich" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(100) NOT NULL,
    "content" JSON NOT NULL
);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """


MODELS_STATE = (
    "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"
    "suZl/+DxhzyoE="
)
