from fastadmin import TortoiseInlineModelAdmin, TortoiseModelAdmin, register

from app.maps.models import Map
from app.records.models import Record, Stat

class MapInline(TortoiseInlineModelAdmin):
    model = Map
    list_display = ("id", "title", "difficulty", "created_at")
    list_display_links = ("title",)
    extra = 0
    fk_name = "creator" 
    ordering = ("-id",)

class UserRecordInline(TortoiseInlineModelAdmin):
    model = Record
    fk_name = "user" 
    list_display = ("map", "pp", "clear_time", "created_at")
    ordering = ("-pp",)
    extra = 0

class UserStatInline(TortoiseInlineModelAdmin):
    model = Stat
    fk_name = "user"
    list_display = ("map", "attempts", "deaths", "is_cleared", "is_loved", "updated_at")

    sortable_fields = ("attempts", "deaths", "updated_at")
    ordering = ("-updated_at",)
    
    list_per_page = 20
    extra = 0
    
    readonly_fields = ("map", "user", "attempts", "deaths", "created_at", "updated_at")

class RecordInline(TortoiseInlineModelAdmin):
    model = Record
    fk_name = "map"
    list_display = ("pp", "user", "deaths", "clear_time", "created_at")
    
    ordering = ("-pp",)
    max_num = 20  
    readonly_fields = ("pp", "user", "map", "deaths", "clear_time", "replay_url", "created_at")
    
    extra = 0

class StatInline(TortoiseInlineModelAdmin):
    model = Stat
    fk_name = "map"
    
    list_display = ("user", "attempts", "deaths", "is_cleared", "is_loved", "updated_at")
    
    ordering = ("-attempts",)
    readonly_fields = ("user", "map", "created_at", "updated_at")
    
    sortable_fields = ("attempts", "deaths")
    list_per_page = 20
    extra = 0