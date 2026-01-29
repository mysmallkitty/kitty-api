from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "map" ADD "map_url" VARCHAR(255) NOT NULL;
        ALTER TABLE "map" ADD "preview_url" VARCHAR(255);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "map" DROP COLUMN "map_url";
        ALTER TABLE "map" DROP COLUMN "preview_url";"""


MODELS_STATE = (
    "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"
    "7HAV5/A8yHbPU="
)
