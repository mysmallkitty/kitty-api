from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "record" ADD "pp" INT;
        ALTER TABLE "record" ADD "rank" INT;
        ALTER TABLE "record" ALTER COLUMN "clear_time" TYPE INT USING "clear_time"::INT;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "record" DROP COLUMN "pp";
        ALTER TABLE "record" DROP COLUMN "rank";
        ALTER TABLE "record" ALTER COLUMN "clear_time" TYPE DOUBLE PRECISION USING "clear_time"::DOUBLE PRECISION;"""


MODELS_STATE = (
    "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"
    "kDrAyaiQOYOMC2xwFe/gD5x9vR"
)
