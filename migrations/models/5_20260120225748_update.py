from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "user" ALTER COLUMN "profile_img_url" DROP NOT NULL;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "user" ALTER COLUMN "profile_img_url" SET NOT NULL;"""


MODELS_STATE = (
    "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"
)
