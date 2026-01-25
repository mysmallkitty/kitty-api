import os

from dotenv import load_dotenv

load_dotenv(".env")

from config.base import *

match os.environ.get("ENVIRONLEVEL", "null"):
    case "PROD":
        from config.prod import *
    case "DEV":
        from config.dev import *
    case "LOCAL":
        from config.local import *
    case _:
        from config.local import *

if PASSWORD_SALT is None or JWT_SECRET_KEY is None:
    raise EnvironmentError("필수 환경 변수(.env)가 설정되지 않았습니다.")


TORTOISE_ORM = {
    "connections": {"default": DB_URL},
    "apps": {
        "models": {
            "models": [
                "aerich.models",
                "app.user.models",
                "app.maps.models",
                "app.records.models",
            ],
            "default_connection": "default",
        },
    },
}
