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
CREATE TABLE IF NOT EXISTS "maps" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "title" VARCHAR(50) NOT NULL UNIQUE,
    "detail" TEXT NOT NULL,
    "level" DOUBLE PRECISION NOT NULL DEFAULT 1,
    "is_ranked" BOOL NOT NULL DEFAULT False,
    "is_wip" BOOL NOT NULL DEFAULT True,
    "map_url" VARCHAR(255) NOT NULL,
    "thumbnail_url" VARCHAR(255),
    "total_deaths" INT NOT NULL DEFAULT 0,
    "total_attempts" INT NOT NULL DEFAULT 0,
    "total_clears" INT NOT NULL DEFAULT 0,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "creator_id" INT NOT NULL REFERENCES "user" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "record" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "deaths" INT NOT NULL DEFAULT 0,
    "time" DOUBLE PRECISION,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "map_id" INT NOT NULL REFERENCES "maps" ("id") ON DELETE CASCADE,
    "user_id" INT NOT NULL REFERENCES "user" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "stat" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "total_deaths" INT NOT NULL DEFAULT 0,
    "total_attempts" INT NOT NULL DEFAULT 0,
    "total_clears" INT NOT NULL DEFAULT 0,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "map_id" INT NOT NULL REFERENCES "maps" ("id") ON DELETE CASCADE,
    "user_id" INT NOT NULL REFERENCES "user" ("id") ON DELETE CASCADE
);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """


MODELS_STATE = (
    "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"
    "pErXuI+vIHltwQfw=="
)
