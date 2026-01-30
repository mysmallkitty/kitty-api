import os
from typing import List
from starlette.requests import Request
from fastapi_admin.app import app
from fastapi_admin.enums import Method
from fastapi_admin.file_upload import FileUpload
from fastapi_admin.resources import Action, Dropdown, Field, Link, Model, ToolbarAction
from fastapi_admin.widgets import displays, filters, inputs

import settings
from app.user.models import User
from app.maps.models import Map
from app.records.models import Record, Stat

upload = FileUpload(uploads_dir=settings.storage_path)

@app.register
class Dashboard(Link):
    label = "Dashboard"
    url = "/admin"
    template = "dashboard.html"
    icon = "fas fa-home"

@app.register
class UserResource(Model):
    label = "User"
    model = User
    page_pre_title = "user list"
    page_title = "user model"

    async def get_toolbar_actions(self, request: Request) -> List[ToolbarAction]:
        return [
            ToolbarAction(label="Go Home", icon="fas fa-home", name="go_home", url="/"),
        ]

    async def get_actions(self, request: Request) -> List[Action]:
        actions = await super().get_actions(request)
        actions.append(
            Action(
                label="Ban/Unban",
                icon="fas fa-ban",
                name="toggle_ban",
                method=Method.PUT,
            )
        )
        return actions

    async def toggle_ban(self, request: Request, pk: int):
        """toggle_ban 액션이 클릭되었을 때 실행되는 로직"""
        user = await self.model.get(id=pk)
        user.is_banned = not user.is_banned
        await user.save()
        return {"message": f"User {user.username} ban status changed to {user.is_banned}"}

    filters = [
      filters.Search(
          name="username",
          label="username",
          search_mode="contains",
          placeholder="Search for username",
          ),
      filters.Datetime(
          name="created_at", 
          label="CreatedAt"
          ),
      ]
    fields = [
        "id",
        "username",
        Field(name="email", label="Email", input_=inputs.Email()),
        "level",
        "exp",
        "country",
        "is_banned",
        "total_deaths",
        "total_attempts",
        "total_clears",
        "total_loved",
        "role",
        "total_pp",
        "created_at",
        "updated_at",
        "last_login_at",
        Field(
            name="profile_img_url",
            label="Profile Image",
            display=displays.Image(width="40"),
            input_=inputs.Image(null=True, upload=upload),
        ),
        "created_at",
    ]

@app.register
class MapResource(Model):
    label = "Maps"
    model = Map
    icon = "fas fa-map"
    filters = [
        filters.Search(name="title", label="Title", search_mode="contains", placeholder="Search title"),
    ]
    fields = [
        "id",
        "title",
        "creator",
        "detail",
        "rating",
        "death_meter",
        "total_deaths",
        "total_attempts",
        "total_clears",
        "loved_count",
        "is_ranked",
        "map_url",
        "preview_url",
        "is_ranked",
        "created_at",
    ]

@app.register
class GameData(Dropdown):
    label = "Game Data"
    icon = "fas fa-chart-bar"

    class RecordResource(Model):
        label = "Records"
        model = Record
        fields = ["id", "user", "map", "clear_time", "deaths", "created_at"]

    class StatResource(Model):
        label = "Stats"
        model = Stat
        fields = ["id", "user", "map", "attempts", "deaths", "is_cleared", "created_at"]

    resources = [RecordResource, StatResource]
