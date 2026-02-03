from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "map" DROP CONSTRAINT IF EXISTS "map_title_key";
        DROP INDEX IF EXISTS "uid_map_title_8e94c7";
        ALTER TABLE "user" ADD "total_loved" INT NOT NULL DEFAULT 0;
        ALTER TABLE "user" ADD "is_banned" BOOL NOT NULL DEFAULT False;
        ALTER TABLE "user" ADD "profile_sprite" VARCHAR(256);
        ALTER TABLE "user" DROP COLUMN "profile_img_url";
        ALTER TABLE "map" RENAME COLUMN "level" TO "rating";
        ALTER TABLE "map" ADD "hash" VARCHAR(64) NOT NULL DEFAULT '';
        ALTER TABLE "map" RENAME COLUMN "preview" TO "preview_url";
        ALTER TABLE "map" RENAME COLUMN "download_count" TO "death_meter";
        ALTER TABLE "map" DROP COLUMN "is_wip";
        ALTER TABLE "record" ALTER COLUMN "pp" TYPE DOUBLE PRECISION USING "pp"::DOUBLE PRECISION;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "map" RENAME COLUMN "death_meter" TO "download_count";
        ALTER TABLE "map" RENAME COLUMN "rating" TO "level";
        ALTER TABLE "map" RENAME COLUMN "preview_url" TO "preview";
        ALTER TABLE "map" ADD "is_wip" BOOL NOT NULL DEFAULT True;
        ALTER TABLE "map" DROP COLUMN "hash";
        ALTER TABLE "user" ADD "profile_img_url" VARCHAR(255);
        ALTER TABLE "user" DROP COLUMN "total_loved";
        ALTER TABLE "user" DROP COLUMN "is_banned";
        ALTER TABLE "user" DROP COLUMN "profile_sprite";
        ALTER TABLE "record" ALTER COLUMN "pp" TYPE INT USING "pp"::INT;
        CREATE UNIQUE INDEX IF NOT EXISTS "uid_map_title_8e94c7" ON "map" ("title");"""


MODELS_STATE = (
    "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"
    "oo0D7OjA2jiAjQOsDZqNA9g4wK7HAZ7/B563p44="
)
