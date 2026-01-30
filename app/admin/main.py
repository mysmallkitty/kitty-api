import sys
import os

# 몽키 패치 온몸비틀기
try:
    import redis.asyncio as redis_asyncio
    sys.modules["aioredis"] = redis_asyncio
except ImportError:
    pass

# 몽키 패치 2 온몸비틀기
import jinja2.ext
if not hasattr(jinja2.ext, 'autoescape'):
    class AutoEscapeExtension(jinja2.ext.Extension):
        def __init__(self, environment):
            super().__init__(environment)
    jinja2.ext.autoescape = AutoEscapeExtension

from fastapi import FastAPI
from fastapi_admin.app import app as admin_app
from fastapi_admin.providers.login import UsernamePasswordProvider

import settings
from app.user.models import User

import app.admin.resources
import app.admin.router

login_provider = UsernamePasswordProvider(
    admin_model=User,
)


async def setup_admin(app: FastAPI):
    redis_client = redis_asyncio.from_url(
        settings.REDIS_URL, decode_responses=True, encoding="utf8"
    )

    await admin_app.configure(
        template_folders=[
            os.path.join(os.path.dirname(__file__), "templates"),
        ], 
        providers=[login_provider],
        redis=redis_client,
    )

    app.mount("/admin", admin_app)
