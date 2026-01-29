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
    "profile_img_url" VARCHAR(255),
    "level" INT NOT NULL DEFAULT 1,
    "exp" INT NOT NULL DEFAULT 0,
    "country" VARCHAR(3),
    "total_deaths" INT NOT NULL DEFAULT 0,
    "total_attempts" INT NOT NULL DEFAULT 0,
    "total_clears" INT NOT NULL DEFAULT 0,
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
    "pp" INT,
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
)
