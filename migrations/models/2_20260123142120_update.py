from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "map" RENAME COLUMN "thumbnail_url" TO "preview";"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "map" RENAME COLUMN "preview" TO "thumbnail_url";"""


MODELS_STATE = (
    "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"
    "x7HODlN2zdzyM="
)
