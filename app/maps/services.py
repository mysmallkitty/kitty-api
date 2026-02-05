from typing import Optional
from app.maps.schemas import MapFilterSchema
from app.maps.models import Map
from app.user.models import User
from app.records.models import Stat

async def get_filtered_maps_service(params: MapFilterSchema, user: Optional[User] = None):
    query = (
        Map.all()
        .select_related("creator")
        .only(
            "id",
            "creator__username",
            "title",
            "rating",
            "is_ranked",
            "loved_count",
            "total_attempts",
            "hash",
        )
    )

    if params.map_id:
        query = query.filter(id=params.map_id)

    if params.title and len(params.title) >= 2:
        query = query.filter(title__istartswith=params.title.strip())

    if params.creator:
        query = query.filter(creator__username__istartswith=params.creator.strip())

    if params.ranked_only:
        query = query.filter(is_ranked=True)

    if params.loved_only:
        if not user:
            return {"total": 0, "items": []}
        
        query = query.filter(
            stats__user_id=user.id,
            stats__is_loved=True,
        ).distinct()

    if params.rating_min is not None:
        query = query.filter(rating__gte=params.rating_min)

    if params.rating_max is not None:
        query = query.filter(rating__lte=params.rating_max)

    total = await query.count()

    sort_map = {
        "latest": "-id",
        "plays": "-total_attempts",
        "loved": "-loved_count",
        "rating": "-rating",
    }

    items = await query.order_by(
        sort_map.get(params.sort, "-id")
    ).offset(params.offset).limit(params.size)

    if user and items:
        map_ids = [item.id for item in items]
        loved_ids = set(
            await Stat.filter(
                user_id=user.id,
                map_id__in=map_ids,
                is_loved=True,
            ).values_list("map_id", flat=True)
        )
        for item in items:
            item.is_loved = item.id in loved_ids

    return {
        "total": total,
        "items": items,
    }
