from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "map" DROP COLUMN "replay_url";"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "map" ADD "replay_url" VARCHAR(255);"""


MODELS_STATE = (
    "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"
    "cBXv4ArjfUCw=="
)
