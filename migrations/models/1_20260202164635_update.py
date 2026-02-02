from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "user" ADD "player_sprite" VARCHAR(81);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "user" DROP COLUMN "player_sprite";"""


MODELS_STATE = (
    "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"
    "=="
)
