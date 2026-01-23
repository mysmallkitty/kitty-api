from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "user" RENAME COLUMN "skill_level" TO "total_pp";"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "user" RENAME COLUMN "total_pp" TO "skill_level";"""


MODELS_STATE = (
    "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"
    "sHsHGAXY8DPP8PsY7U4Q=="
)
