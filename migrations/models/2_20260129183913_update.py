from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "user" ADD "total_loved" INT NOT NULL DEFAULT 0;
        ALTER TABLE "user" ADD "total_downloads" INT NOT NULL DEFAULT 0;
        ALTER TABLE "user" ADD "is_banned" INT NOT NULL DEFAULT 0;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "user" DROP COLUMN "total_loved";
        ALTER TABLE "user" DROP COLUMN "total_downloads";
        ALTER TABLE "user" DROP COLUMN "is_banned";"""


MODELS_STATE = (
    "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"
    "RKLX"
)
