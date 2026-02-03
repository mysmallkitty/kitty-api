from fastadmin import TortoiseModelAdmin, register, action, display
from app.admin.inline import MapInline, RecordInline, StatInline, UserRecordInline, UserStatInline
from app.admin.mixins import RolePermissionMixin
from app.maps.models import Map
from app.records.models import Record, Stat
from app.user.models import Roles, User

@register(User)
class UserAdmin(RolePermissionMixin,TortoiseModelAdmin):
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
    fieldsets = (
            (None, {
                "fields": ["username", "email", "role", "profile_sprite", "country"] 
            }),
            ("stat", {
                "fields": [ 
                    "level", "exp",
                    "total_pp",
                    "total_clears", "total_attempts", "total_deaths",
                ]
            }),
            ("system", {
                "fields": ["is_banned", "last_login_at", "created_at", "updated_at"],  
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
    
    actions = ("make_mod", "make_rm", "make_lv", "make_user", "ban_users", "unban_users")

    @action(description="promote to MOD")
    async def make_mod(self, *args, **kwargs):
        ids = next((arg for arg in args if isinstance(arg, list)), None)

        if ids:
            await User.filter(id__in=ids).update(role=Roles.MOD.value)

    @action(description="Promote to RM")
    async def make_rm(self, *args, **kwargs):
        ids = next((arg for arg in args if isinstance(arg, list)), None)

        if ids:
            await User.filter(id__in=ids).update(role=Roles.RM.value)

    @action(description="Promote to LV")
    async def make_lv(self, *args, **kwargs):
        ids = next((arg for arg in args if isinstance(arg, list)), None)

        if ids:
            await User.filter(id__in=ids).update(role=Roles.LV.value)

    @action(description="Make regular User")
    async def make_user(self, *args, **kwargs):
        ids = next((arg for arg in args if isinstance(arg, list)), None)

        if ids:
            await User.filter(id__in=ids).update(role=Roles.USER.value)

    @action(description="Ban Users")
    async def ban_users(self, *args, **kwargs):
        ids = next((arg for arg in args if isinstance(arg, list)), None)

        if ids:
            await User.filter(id__in=ids).update(is_banned=True)
    
    @action(description="Unban Users")
    async def unban_users(self, *args, **kwargs):
        ids = next((arg for arg in args if isinstance(arg, list)), None)
        
        if ids:
            await User.filter(id__in=ids).update(is_banned=False)

    allowed_roles = [Roles.ADMIN.value, Roles.MOD.value]

    async def has_add_permission(self, user_id=None):
        return await self._has_role(user_id)

    async def has_change_permission(self, user_id=None):
        return await self._has_role(user_id)
    
    async def has_delete_permission(self, user_id=None):
        return await self._has_role(user_id)
    
    async def has_export_permission(self, user_id=None):
        return await self._has_role(user_id)
    


@register(Map)
class MapAdmin(RolePermissionMixin, TortoiseModelAdmin):
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
    search_fields = ("title",)
    ordering = ("-id",)
    inlines = (
        RecordInline,
        StatInline,
        )

    fieldsets = (
        ("Metadata", {
            "fields": ["title", "detail", "creator", "rating", "death_meter"] 
        }),
        ("Status & Files", {
            "fields": ["is_ranked", "map_url", "preview_url", "hash"]  
        }),
        ("Stats", {
            "fields": ["total_clears", "total_attempts", "total_deaths", "loved_count"], 
            "classes": ("collapse",)
        }),
        ("Timestamps", {
            "fields": ["created_at", "updated_at"], 
            "classes": ("collapse",)
        }),
    )

    readonly_fields = ("id", "created_at", "updated_at", "hash")

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

    allowed_roles = [Roles.ADMIN.value, Roles.MOD.value, Roles.RM.value]

    async def has_add_permission(self, user_id=None):
        return await self._has_role(user_id)

    async def has_change_permission(self, user_id=None):
        return await self._has_role(user_id)
    
    async def has_delete_permission(self, user_id=None):
        return await self._has_role(user_id)
    
    async def has_export_permission(self, user_id=None):
        return await self._has_role(user_id)
    


@register(Record)
class RecordAdmin(RolePermissionMixin, TortoiseModelAdmin):
    list_display = ("id", "map_title", "username", "pp", "get_country", "created_at")
    list_display_links = ("id",)
    
    ordering = ("-pp",)

    @display
    async def get_country(self, obj):
        user = await obj.user.first()
        return user.country if user else None
    
    @display
    async def username(self, obj):
        user = await obj.user.first()
        return user.username if user else None
    
    @display
    async def map_title(self, obj):
        m = await obj.map.first()
        return m.title if m else None

    allowed_roles = [Roles.ADMIN.value, Roles.MOD.value]

    async def has_add_permission(self, user_id=None):
        return await self._has_role(user_id)

    async def has_change_permission(self, user_id=None):
        return await self._has_role(user_id)
    
    async def has_delete_permission(self, user_id=None):
        return await self._has_role(user_id)
    
    async def has_export_permission(self, user_id=None):
        return await self._has_role(user_id)
    


@register(Stat)
class StatAdmin(RolePermissionMixin, TortoiseModelAdmin):
    list_display = ("id", "map_title", "username", "is_loved", "is_cleared")
    list_filter = ("is_cleared", "is_loved")

    @display
    async def username(self, obj):
        user = await obj.user.first()
        return user.username if user else None
    
    @display
    async def map_title(self, obj):
        m = await obj.map.first()
        return m.title if m else None

    allowed_roles = [Roles.ADMIN.value, Roles.MOD.value]

    async def has_add_permission(self, user_id=None):
        return await self._has_role(user_id)

    async def has_change_permission(self, user_id=None):
        return await self._has_role(user_id)
    
    async def has_delete_permission(self, user_id=None):
        return await self._has_role(user_id)
    
    async def has_export_permission(self, user_id=None):
        return await self._has_role(user_id)
    
