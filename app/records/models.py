from tortoise import fields
from tortoise.models import Model


class Stat(Model):

    id = fields.IntField(pk=True)
    map = fields.ForeignKeyField("models.Map", related_name="stats")
    user = fields.ForeignKeyField("models.User", related_name="stats")
    deaths = fields.IntField(default=0)
    attempts = fields.IntField(default=0)
    is_cleared = fields.BooleanField(default=False)
    is_loved = fields.BooleanField(default=False)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        unique_together = ("user", "map") 


class Record(Model):

    id = fields.IntField(pk=True)
    map = fields.ForeignKeyField("models.Map", related_name="records")
    user = fields.ForeignKeyField("models.User", related_name="records")
    deaths = fields.IntField(default=0)
    clear_time = fields.FloatField(null=True)
    replay_url = fields.CharField(max_length=255)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
