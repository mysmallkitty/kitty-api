from typing import Optional
from app.maps.schemas import MapFilterSchema
from app.maps.models import Map
from app.user.models import User

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

    return {
        "total": total,
        "items": items,
    }