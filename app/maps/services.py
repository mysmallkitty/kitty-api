from tortoise.expressions import F

from app.maps.dependencies import MapFilterParams
from app.maps.models import Map


async def get_filtered_maps(params: MapFilterParams):
    query = (
        Map.all()
        .only(
            "id",
            "creator_id",
            "title",
            "level",
            "preview",
            "loved_count",
            "download_count",
            "is_ranked",
        )
        .prefetch_related("creator")
    )

    if params.title:
        query = query.filter(title__icontains=params.title.strip())
    if params.creator:
        query = query.filter(creator__username__icontains=params.creator.strip())

    sort_map = {
        "latest": "-id",
        "downloads": "-download_count",
        "difficulty": "-level",
        "loved": "-loved_count",
    }
    query = query.order_by(sort_map.get(params.sort, "-id"))

    return await query.offset(params.offset).limit(params.size)
