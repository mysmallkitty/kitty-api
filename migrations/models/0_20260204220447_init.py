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
    "profile_sprite" VARCHAR(256),
    "player_sprite" VARCHAR(81),
    "level" INT NOT NULL DEFAULT 1,
    "exp" INT NOT NULL DEFAULT 0,
    "country" VARCHAR(3),
    "is_banned" BOOL NOT NULL DEFAULT False,
    "total_deaths" INT NOT NULL DEFAULT 0,
    "total_attempts" INT NOT NULL DEFAULT 0,
    "total_clears" INT NOT NULL DEFAULT 0,
    "total_loved" INT NOT NULL DEFAULT 0,
    "role" VARCHAR(10) NOT NULL DEFAULT 'user',
    "total_pp" DOUBLE PRECISION NOT NULL DEFAULT 0,
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
    "title" VARCHAR(50) NOT NULL,
    "detail" TEXT NOT NULL,
    "rating" DOUBLE PRECISION NOT NULL DEFAULT 1,
    "death_meter" INT NOT NULL DEFAULT 0,
    "is_ranked" BOOL NOT NULL DEFAULT False,
    "hash" VARCHAR(64) NOT NULL DEFAULT '',
    "total_deaths" INT NOT NULL DEFAULT 0,
    "total_attempts" INT NOT NULL DEFAULT 0,
    "total_clears" INT NOT NULL DEFAULT 0,
    "loved_count" INT NOT NULL DEFAULT 0,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "creator_id" INT NOT NULL REFERENCES "user" ("id") ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS "idx_map_title_8e94c7" ON "map" ("title");
CREATE INDEX IF NOT EXISTS "idx_map_rating_435db2" ON "map" ("rating");
CREATE INDEX IF NOT EXISTS "idx_map_is_rank_101689" ON "map" ("is_ranked");
CREATE INDEX IF NOT EXISTS "idx_map_creator_95cc5a" ON "map" ("creator_id");
CREATE TABLE IF NOT EXISTS "record" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "deaths" INT NOT NULL DEFAULT 0,
    "clear_time" INT,
    "pp" DOUBLE PRECISION,
    "replay_url" VARCHAR(255) NOT NULL,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "map_id" INT NOT NULL REFERENCES "map" ("id") ON DELETE CASCADE,
    "user_id" INT NOT NULL REFERENCES "user" ("id") ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS "idx_record_map_id_eefee9" ON "record" ("map_id");
CREATE INDEX IF NOT EXISTS "idx_record_user_id_ad64ea" ON "record" ("user_id");
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
);
CREATE INDEX IF NOT EXISTS "idx_stat_is_love_4c4fbd" ON "stat" ("is_loved");
CREATE INDEX IF NOT EXISTS "idx_stat_map_id_9d7596" ON "stat" ("map_id");
CREATE INDEX IF NOT EXISTS "idx_stat_user_id_45b8cd" ON "stat" ("user_id");
CREATE INDEX IF NOT EXISTS "idx_stat_user_id_9c4116" ON "stat" ("user_id", "is_loved");"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """


MODELS_STATE = (
    "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"
    "5L5BU="
)
