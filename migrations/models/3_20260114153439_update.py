from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "map" ADD "download_count" INT NOT NULL DEFAULT 0;
        ALTER TABLE "map" ADD "loved_count" INT NOT NULL DEFAULT 0;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "map" DROP COLUMN "download_count";
        ALTER TABLE "map" DROP COLUMN "loved_count";"""


MODELS_STATE = (
    "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"
    "Q9SXP4XMSL8="
)
