from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "map" ALTER COLUMN "level" TYPE DOUBLE PRECISION USING "level"::DOUBLE PRECISION;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "map" ALTER COLUMN "level" TYPE INT USING "level"::INT;"""


MODELS_STATE = (
    "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"
    "JoNg5g4wDbHgd4+Q1yjNdH"
)
