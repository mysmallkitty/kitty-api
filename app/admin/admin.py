from fastadmin import TortoiseModelAdmin, register, action
from fastapi import Request
from app.admin.inline import MapInline, RecordInline, StatInline, UserRecordInline, UserStatInline
from app.maps.models import Map
from app.records.models import Record, Stat
from app.user.models import Roles, User
from fastadmin import DashboardWidgetAdmin, DashboardWidgetType, register_widget

@register_widget
class UsersDashboardWidgetAdmin(DashboardWidgetAdmin):
    dashboard_widgets = (
        DashboardWidgetAdmin(
            widget_type=DashboardWidgetType.STAT,
            title="Total Users",
            query=lambda: User.all().count(),
        ),
        DashboardWidgetAdmin(
            widget_type=DashboardWidgetType.STAT,
            title="Total Clears",
            query=lambda: Record.all().count(),
        ),
        DashboardWidgetAdmin(
            widget_type=DashboardWidgetType.CHART,
            title="Top Players by PP",
            query=lambda: User.all().order_by("-total_pp").limit(10),
        ),
    )

@register(User)
class UserAdmin(TortoiseModelAdmin):
    list_display = (
        "id", 
        "username", 
        "role",
        "email",
        "total_pp",
        "level",
        "country",
        "is_banned",
        )
    list_display_links = (
        "username",
        )
    list_editable = ("is_banned", "role")
    fieldsets = (
            (None, {
                "fields": ("username", "email", "role", "profile_sprite", "country")
            }),
            ("stat", {
                "fields": (
                    ("level", "exp"), 
                    "total_pp",
                    ("total_clears", "total_attempts", "total_deaths"),
                    "total_loved"
                )
            }),
            ("system", {
                "fields": ("is_banned", "last_login_at", "created_at", "updated_at"),
                "classes": ("collapse",)
            }),
        )
    readonly_fields = (
        "id",
        "username",
        "created_at",
        )
    list_filter = ("role",)                   
    search_fields = ("username",)           
    exclude = ("password",)
    inlines = (
        MapInline,
        UserRecordInline,
        UserStatInline,
        )

    async def authenticate(self, username: str, password: str) -> int | None:
        user = await User.filter(username=username, role__in=[Roles.ADMIN, Roles.MOD, Roles.RM]).first()
        if not user or not user.verify_password(password):
            return None
        return user.id

    async def has_add_permission(self, request=None, user_id=None) -> bool:
        if not request or not hasattr(request, "user") or not request.user:
            return False
        return request.user.role in [Roles.ADMIN.value, Roles.MOD.value]

    async def has_change_permission(self, request=None, user_id=None) -> bool:
        if not request or not hasattr(request, "user") or not request.user:
            return False
        return request.user.role in [Roles.ADMIN.value, Roles.MOD.value]

    async def has_delete_permission(self, request=None, user_id=None) -> bool:
        if not request or not hasattr(request, "user") or not request.user:
            return False
        return request.user.role in [Roles.ADMIN.value, Roles.MOD.value]

    async def has_export_permission(self, request=None, user_id=None) -> bool:
        if not request or not hasattr(request, "user") or not request.user:
            return False
        return request.user.role in [Roles.ADMIN.value, Roles.MOD.value]
    
    actions = ("make_mod", "make_user", "ban_users", "unban_users")

    @action(description="Promote to MOD")
    async def make_mod(self, *args, **kwargs):
        ids = next((arg for arg in args if isinstance(arg, list)), None)

        if ids:
            await User.filter(id__in=ids).update(role=Roles.MOD.value)

    @action(description="Make regular User")
    async def make_user(self, *args, **kwargs):
        ids = next((arg for arg in args if isinstance(arg, list)), None)

        if ids:
            await User.filter(id__in=ids).update(role=Roles.USER.value)

    @action(description="Ban selected Users")
    async def ban_users(self, *args, **kwargs):
        ids = next((arg for arg in args if isinstance(arg, list)), None)

        if ids:
            await User.filter(id__in=ids).update(is_banned=True)
    
    @action(description="Unban selected Users")
    async def unban_users(self, *args, **kwargs):
        ids = next((arg for arg in args if isinstance(arg, list)), None)
        
        if ids:
            await User.filter(id__in=ids).update(is_banned=False)


@register(Map)
class MapAdmin(TortoiseModelAdmin):
    list_display = (
        "id", 
        "title", 
        "creator", 
        "rating", 
        "is_ranked", 
        "total_clears", 
        "created_at"
        )
    list_display_links = ("title",)
    list_filter = ("is_ranked", "rating")
    search_fields = ("title", "creator__username")
    ordering = ("-id",)
    inlines = (
        RecordInline,
        StatInline,
        )

    fieldsets = (
        ("Metadata", {
            "fields": ("title", "detail", "creator", "rating", "death_meter")
        }),
        ("Status & Files", {
            "fields": ("is_ranked", "map_url", "preview_url", "hash")
        }),
        ("Stats", {
            "fields": (("total_clears", "total_attempts", "total_deaths"), "loved_count"),
            "classes": ("collapse",)
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",)
        }),
    )

    readonly_fields = ("id", "created_at", "updated_at", "hash")


    async def has_add_permission(self, request=None, user_id=None) -> bool:
        if not request or not hasattr(request, "user") or not request.user:
            return False
        return request.user.role in [Roles.ADMIN.value, Roles.MOD.value]

    async def has_change_permission(self, request=None, user_id=None) -> bool:
        if not request or not hasattr(request, "user") or not request.user:
            return False
        return request.user.role in [Roles.ADMIN.value, Roles.MOD.value, Roles.RM.value]

    async def has_delete_permission(self, request=None, user_id=None) -> bool:
        if not request or not hasattr(request, "user") or not request.user:
            return False
        return request.user.role in [Roles.ADMIN.value, Roles.MOD.value]

    async def has_export_permission(self, request=None, user_id=None) -> bool:
        if not request or not hasattr(request, "user") or not request.user:
            return False
        return request.user.role in [Roles.ADMIN.value, Roles.MOD.value]

    actions = ("set_ranked", "unset_ranked")

    @action(description="set Ranked Status")
    async def set_ranked(self, *args, **kwargs):
        ids = next((arg for arg in args if isinstance(arg, list)), None)
        if ids:
            await Map.filter(id__in=ids).update(is_ranked=True)

    @action(description="Unset Ranked Status")
    async def unset_ranked(self, *args, **kwargs):
        ids = next((arg for arg in args if isinstance(arg, list)), None)
        if ids:
            await Map.filter(id__in=ids).update(is_ranked=False)

@register(Record)
class RecordAdmin(TortoiseModelAdmin):
    list_display = ("id", "map", "user_link", "pp", "get_country", "created_at")
    
    list_filter = ("user__country", "map__is_ranked") 
    search_fields = ("user__username", "map__title")
    
    ordering = ("-pp",)

    def get_country(self, obj):
        return obj.user.country
    get_country.short_description = "country"

    def user_link(self, obj):
        from markupsafe import mark_safe
        return mark_safe(f'<a href="/admin/user/edit/{obj.user.id}">{obj.user.username}</a>')
    user_link.short_description = "username"

@register(Stat)
class StatAdmin(TortoiseModelAdmin):
    list_display = ("id", "map", "user", "is_loved", "is_cleared")
    list_filter = ("user__country", "is_cleared", "is_loved")
    search_fields = ("map__title", "user__username")

    def get_country(self, obj):
        return obj.user.country
    get_country.short_description = "country"