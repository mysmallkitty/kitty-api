from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "record" ADD "replay_url" VARCHAR(255) NOT NULL;
        ALTER TABLE "record" RENAME COLUMN "time" TO "clear_time";
        ALTER TABLE "stat" ADD "is_loved" BOOL NOT NULL DEFAULT False;
        ALTER TABLE "stat" RENAME COLUMN "total_attempts" TO "attempts";
        ALTER TABLE "stat" RENAME COLUMN "total_deaths" TO "deaths";
        ALTER TABLE "stat" ADD "is_cleared" BOOL NOT NULL DEFAULT False;
        ALTER TABLE "stat" DROP COLUMN "total_clears";
        CREATE UNIQUE INDEX IF NOT EXISTS "uid_stat_user_id_b02e97" ON "stat" ("user_id", "map_id");"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP INDEX IF EXISTS "uid_stat_user_id_b02e97";
        ALTER TABLE "stat" RENAME COLUMN "deaths" TO "total_deaths";
        ALTER TABLE "stat" RENAME COLUMN "attempts" TO "total_attempts";
        ALTER TABLE "stat" ADD "total_clears" INT NOT NULL DEFAULT 0;
        ALTER TABLE "stat" DROP COLUMN "is_loved";
        ALTER TABLE "stat" DROP COLUMN "is_cleared";
        ALTER TABLE "record" RENAME COLUMN "clear_time" TO "time";
        ALTER TABLE "record" DROP COLUMN "replay_url";"""


MODELS_STATE = (
    "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"
)
