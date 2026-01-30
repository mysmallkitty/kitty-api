from fastapi import Depends
from starlette.requests import Request
from fastapi_admin.app import app
from fastapi_admin.depends import get_resources
from fastapi_admin.template import templates

from app.user.models import User
from app.maps.models import Map
from app.records.models import Record

@app.get("/")
async def home(
    request: Request,
    resources=Depends(get_resources),
):
    return templates.TemplateResponse(
        "dashboard.html",
        context={
            "request": request,
            "resources": resources,
            "resource_label": "Dashboard",
            "page_pre_title": "overview",
            "page_title": "Dashboard",
            "user_count": await User.all().count(),
            "map_count": await Map.all().count(),
            "record_count": await Record.all().count(),
        },
    )
