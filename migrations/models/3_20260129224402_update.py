from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "map" ADD "hash" VARCHAR(64) NOT NULL DEFAULT '';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "map" DROP COLUMN "hash";"""


MODELS_STATE = (
    "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"
    "AHs6sNoPoP0AG4Om/QDaD7DvfoDX/wHDewbf"
)
