from tortoise import fields
from tortoise.models import Model

class Map(Model):
    
    # metadata
    id = fields.IntField(pk=True)
    title = fields.CharField(max_length=50, unique=True)
    detail = fields.TextField()
    level = fields.FloatField(default=1)
    creator = fields.ForeignKeyField("models.User", related_name="maps")

    # status
    is_ranked = fields.BooleanField(default=False)
    is_wip = fields.BooleanField(default=True)

    # file paths
    map_url = fields.CharField(max_length=255)
    thumbnail_url = fields.CharField(max_length=255, null=True)

    # stats
    total_deaths = fields.IntField(default=0)
    total_attempts = fields.IntField(default=0)
    total_clears = fields.IntField(default=0)

    # timestamps
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    def __str__(self) -> str:
        return self.title

class Stat(Model):

    id = fields.IntField(pk=True)
    map = fields.ForeignKeyField("models.Map", related_name="stats")
    user = fields.ForeignKeyField("models.User", related_name="stats")
    total_deaths = fields.IntField(default=0)
    total_attempts = fields.IntField(default=0)
    total_clears = fields.IntField(default=0)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

class Record(Model):

    id = fields.IntField(pk=True)
    map = fields.ForeignKeyField("models.Map", related_name="stats")
    user = fields.ForeignKeyField("models.User", related_name="stats")
    deaths = fields.IntField(default=0)
    time = fields.FloatField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)