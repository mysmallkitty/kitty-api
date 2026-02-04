from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "map" DROP COLUMN "map_url";
        ALTER TABLE "map" DROP COLUMN "preview_url";
        ALTER TABLE "record" DROP COLUMN "rank";
        ALTER TABLE "record" ALTER COLUMN "pp" TYPE INT USING "pp"::INT;
        CREATE INDEX IF NOT EXISTS "idx_map_title_8e94c7" ON "map" ("title");
        CREATE INDEX IF NOT EXISTS "idx_map_is_rank_101689" ON "map" ("is_ranked");
        CREATE INDEX IF NOT EXISTS "idx_map_rating_435db2" ON "map" ("rating");
        CREATE INDEX IF NOT EXISTS "idx_map_creator_95cc5a" ON "map" ("creator_id");
        CREATE INDEX IF NOT EXISTS "idx_record_map_id_eefee9" ON "record" ("map_id");
        CREATE INDEX IF NOT EXISTS "idx_record_user_id_ad64ea" ON "record" ("user_id");
        CREATE INDEX IF NOT EXISTS "idx_stat_user_id_9c4116" ON "stat" ("user_id", "is_loved");
        CREATE INDEX IF NOT EXISTS "idx_stat_map_id_9d7596" ON "stat" ("map_id");
        CREATE INDEX IF NOT EXISTS "idx_stat_is_love_4c4fbd" ON "stat" ("is_loved");
        CREATE INDEX IF NOT EXISTS "idx_stat_user_id_45b8cd" ON "stat" ("user_id");"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP INDEX IF EXISTS "idx_record_user_id_ad64ea";
        DROP INDEX IF EXISTS "idx_record_map_id_eefee9";
        DROP INDEX IF EXISTS "idx_stat_user_id_45b8cd";
        DROP INDEX IF EXISTS "idx_stat_is_love_4c4fbd";
        DROP INDEX IF EXISTS "idx_stat_map_id_9d7596";
        DROP INDEX IF EXISTS "idx_stat_user_id_9c4116";
        DROP INDEX IF EXISTS "idx_map_creator_95cc5a";
        DROP INDEX IF EXISTS "idx_map_rating_435db2";
        DROP INDEX IF EXISTS "idx_map_is_rank_101689";
        DROP INDEX IF EXISTS "idx_map_title_8e94c7";
        ALTER TABLE "map" ADD "map_url" VARCHAR(255) NOT NULL;
        ALTER TABLE "map" ADD "preview_url" VARCHAR(255);
        ALTER TABLE "user" DROP COLUMN "player_sprite";
        ALTER TABLE "record" ADD "rank" INT;
        ALTER TABLE "record" ALTER COLUMN "pp" TYPE DOUBLE PRECISION USING "pp"::DOUBLE PRECISION;"""


MODELS_STATE = (
    "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"
    "xP"
)
