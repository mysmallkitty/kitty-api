from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "aerich" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(100) NOT NULL,
    "content" JSONB NOT NULL
);
CREATE TABLE IF NOT EXISTS "user" (
    "id" SERIAL NOT NULL PRIMARY KEY,
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
    "skill_level" DOUBLE PRECISION NOT NULL DEFAULT 0,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "last_login_at" TIMESTAMPTZ
);
CREATE TABLE IF NOT EXISTS "friendship" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "friend_id" INT NOT NULL REFERENCES "user" ("id") ON DELETE CASCADE,
    "user_id" INT NOT NULL REFERENCES "user" ("id") ON DELETE CASCADE,
    CONSTRAINT "uid_friendship_user_id_4038a2" UNIQUE ("user_id", "friend_id")
);
CREATE TABLE IF NOT EXISTS "map" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "title" VARCHAR(50) NOT NULL UNIQUE,
    "detail" TEXT NOT NULL,
    "level" INT NOT NULL DEFAULT 1,
    "is_ranked" BOOL NOT NULL DEFAULT False,
    "is_wip" BOOL NOT NULL DEFAULT True,
    "map_url" VARCHAR(255) NOT NULL,
    "thumbnail_url" VARCHAR(255),
    "replay_url" VARCHAR(255),
    "total_deaths" INT NOT NULL DEFAULT 0,
    "total_attempts" INT NOT NULL DEFAULT 0,
    "total_clears" INT NOT NULL DEFAULT 0,
    "loved_count" INT NOT NULL DEFAULT 0,
    "download_count" INT NOT NULL DEFAULT 0,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "creator_id" INT NOT NULL REFERENCES "user" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "record" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "deaths" INT NOT NULL DEFAULT 0,
    "clear_time" INT,
    "rank" INT,
    "pp" INT,
    "replay_url" VARCHAR(255) NOT NULL,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "map_id" INT NOT NULL REFERENCES "map" ("id") ON DELETE CASCADE,
    "user_id" INT NOT NULL REFERENCES "user" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "stat" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "deaths" INT NOT NULL DEFAULT 0,
    "attempts" INT NOT NULL DEFAULT 0,
    "is_cleared" BOOL NOT NULL DEFAULT False,
    "is_loved" BOOL NOT NULL DEFAULT False,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "map_id" INT NOT NULL REFERENCES "map" ("id") ON DELETE CASCADE,
    "user_id" INT NOT NULL REFERENCES "user" ("id") ON DELETE CASCADE,
    CONSTRAINT "uid_stat_user_id_b02e97" UNIQUE ("user_id", "map_id")
);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """


MODELS_STATE = (
    "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"
    "EzcQATB9j2OMDLH4LkPws="
)
