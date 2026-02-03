import os
from pathlib import Path
from fastadmin.settings import settings
from fastapi.staticfiles import StaticFiles
from fastadmin import fastapi_app as admin_app

admin_app.mount(
    "/admin-custom-static",  
    StaticFiles(directory=Path(__file__).parent / "static"),
    name="admin-custom-static",
)

settings.ADMIN_SITE_NAME = ""
settings.ADMIN_PRIMARY_COLOR = "#F8ABF8"
settings.ADMIN_USER_MODEL = "User"
settings.ADMIN_USER_MODEL_USERNAME_FIELD = "username"
settings.ADMIN_SITE_HEADER_LOGO = "/admin/admin-custom-static/admin_header_logo.png" 
settings.ADMIN_SITE_SIGN_IN_LOGO = "/admin/admin-custom-static/admin_logo.png"
settings.ADMIN_SITE_FAVICON = "/admin/admin-custom-static/admin_header_logo.png"
settings.ADMIN_SECRET_KEY = os.environ["JWT_SECRET_KEY"]

__all__ = ["admin_app"]