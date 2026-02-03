from tortoise import fields
from tortoise.models import Model


class Map(Model):

    # metadata
    id = fields.IntField(pk=True)
    title = fields.CharField(max_length=50)
    detail = fields.TextField()

    rating = fields.FloatField(default=1.0)
    death_meter = fields.IntField(
        default=0
    )  # expected deaths per clear (for calculate pp) , 예상되는 죽음 횟수
    creator = fields.ForeignKeyField("models.User", related_name="maps")

    # status
    is_ranked = fields.BooleanField(default=False)

    # cache
    hash = fields.CharField(max_length=64, default="")
    # stats
    total_deaths = fields.IntField(default=0)
    total_attempts = fields.IntField(default=0)
    total_clears = fields.IntField(default=0)
    loved_count = fields.IntField(default=0)

    # timestamps
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    def __str__(self) -> str:
        return self.title



