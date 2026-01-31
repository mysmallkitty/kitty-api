from fastapi import Depends, Form
from starlette.requests import Request

from aioredis import Redis
from fastapi_admin import constants
from fastapi_admin.depends import get_current_admin, get_resources, get_redis
from fastapi_admin.i18n import _
from fastapi_admin.models import AbstractAdmin
from fastapi_admin.providers.login import UsernamePasswordProvider
from fastapi_admin.template import templates
from fastapi_admin.utils import check_password

PBKDF2_PREFIX = "$pbkdf2-sha256$"


def _is_pbkdf2_hash(value: str) -> bool:
    return isinstance(value, str) and value.startswith(PBKDF2_PREFIX)


class LoginProvider(UsernamePasswordProvider):
    async def pre_save_admin(self, _, instance: AbstractAdmin, using_db, update_fields):
        if hasattr(instance, "set_password"):
            if instance.password and _is_pbkdf2_hash(instance.password):
                return
            instance.set_password(instance.password)
            return
        await super().pre_save_admin(_, instance, using_db, update_fields)

    async def login(self, request: Request, redis: Redis = Depends(get_redis)):
        form = await request.form()
        username = form.get("username")
        password = form.get("password")
        remember_me = form.get("remember_me")
        admin = await self.admin_model.get_or_none(username=username)
        valid = False
        if admin:
            if hasattr(admin, "verify_password"):
                valid = admin.verify_password(password)
            else:
                valid = check_password(password, admin.password)
        if not valid:
            from starlette.status import HTTP_401_UNAUTHORIZED

            return templates.TemplateResponse(
                self.template,
                status_code=HTTP_401_UNAUTHORIZED,
                context={"request": request, "error": _("login_failed")},
            )
        import uuid
        from starlette.responses import RedirectResponse
        from starlette.status import HTTP_303_SEE_OTHER

        response = RedirectResponse(url=request.app.admin_path, status_code=HTTP_303_SEE_OTHER)
        if remember_me == "on":
            expire = 3600 * 24 * 30
            response.set_cookie("remember_me", "on")
        else:
            expire = 3600
            response.delete_cookie("remember_me")
        token = uuid.uuid4().hex
        response.set_cookie(
            self.access_token,
            token,
            expires=expire,
            path=request.app.admin_path,
            httponly=True,
        )
        await redis.set(constants.LOGIN_USER.format(token=token), admin.pk, expire=expire)
        return response

    async def password(
        self,
        request: Request,
        old_password: str = Form(...),
        new_password: str = Form(...),
        re_new_password: str = Form(...),
        admin: AbstractAdmin = Depends(get_current_admin),
        resources=Depends(get_resources),
    ):
        return await self.logout(request)
