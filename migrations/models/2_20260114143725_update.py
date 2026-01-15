from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "user" ADD "profile_img_url" VARCHAR(255) NOT NULL;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "user" DROP COLUMN "profile_img_url";"""


MODELS_STATE = (
    "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"
)
