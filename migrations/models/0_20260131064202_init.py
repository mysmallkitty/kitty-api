from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "aerich" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(100) NOT NULL,
    "content" JSON NOT NULL
);
CREATE TABLE IF NOT EXISTS "user" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "username" VARCHAR(50) NOT NULL UNIQUE,
    "password" VARCHAR(255) NOT NULL,
    "email" VARCHAR(100) NOT NULL,
    "profile_sprite" VARCHAR(256),
    "level" INT NOT NULL DEFAULT 1,
    "exp" INT NOT NULL DEFAULT 0,
    "country" VARCHAR(3),
    "is_banned" INT NOT NULL DEFAULT 0,
    "total_deaths" INT NOT NULL DEFAULT 0,
    "total_attempts" INT NOT NULL DEFAULT 0,
    "total_clears" INT NOT NULL DEFAULT 0,
    "total_loved" INT NOT NULL DEFAULT 0,
    "role" VARCHAR(10) NOT NULL DEFAULT 'user',
    "total_pp" REAL NOT NULL DEFAULT 0,
    "created_at" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "last_login_at" TIMESTAMP
);
CREATE TABLE IF NOT EXISTS "friendship" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "created_at" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "friend_id" INT NOT NULL REFERENCES "user" ("id") ON DELETE CASCADE,
    "user_id" INT NOT NULL REFERENCES "user" ("id") ON DELETE CASCADE,
    CONSTRAINT "uid_friendship_user_id_4038a2" UNIQUE ("user_id", "friend_id")
);
CREATE TABLE IF NOT EXISTS "map" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "title" VARCHAR(50) NOT NULL,
    "detail" TEXT NOT NULL,
    "rating" REAL NOT NULL DEFAULT 1,
    "death_meter" INT NOT NULL DEFAULT 0,
    "is_ranked" INT NOT NULL DEFAULT 0,
    "map_url" VARCHAR(255) NOT NULL,
    "preview_url" VARCHAR(255),
    "hash" VARCHAR(64) NOT NULL DEFAULT '',
    "total_deaths" INT NOT NULL DEFAULT 0,
    "total_attempts" INT NOT NULL DEFAULT 0,
    "total_clears" INT NOT NULL DEFAULT 0,
    "loved_count" INT NOT NULL DEFAULT 0,
    "created_at" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "creator_id" INT NOT NULL REFERENCES "user" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "record" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "deaths" INT NOT NULL DEFAULT 0,
    "clear_time" INT,
    "rank" INT,
    "pp" REAL,
    "replay_url" VARCHAR(255) NOT NULL,
    "created_at" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "map_id" INT NOT NULL REFERENCES "map" ("id") ON DELETE CASCADE,
    "user_id" INT NOT NULL REFERENCES "user" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "stat" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "deaths" INT NOT NULL DEFAULT 0,
    "attempts" INT NOT NULL DEFAULT 0,
    "is_cleared" INT NOT NULL DEFAULT 0,
    "is_loved" INT NOT NULL DEFAULT 0,
    "created_at" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "map_id" INT NOT NULL REFERENCES "map" ("id") ON DELETE CASCADE,
    "user_id" INT NOT NULL REFERENCES "user" ("id") ON DELETE CASCADE,
    CONSTRAINT "uid_stat_user_id_b02e97" UNIQUE ("user_id", "map_id")
);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """


MODELS_STATE = (
    "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"
    "oo0D7OjA2jiAjQOsDZqNA9g4wK7HAZ7/B563p44="
)
