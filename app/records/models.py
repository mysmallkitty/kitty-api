from tortoise import fields
from tortoise.models import Model

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
    map = fields.ForeignKeyField("models.Map", related_name="records")
    user = fields.ForeignKeyField("models.User", related_name="records")
    deaths = fields.IntField(default=0)
    time = fields.FloatField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)