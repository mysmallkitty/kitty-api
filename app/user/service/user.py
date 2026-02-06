

from typing import Optional
from app.records.redis_services import ranking_service
from app.user.models import Friendship, User
from app.user.schemas.user import UserFilterSchema


async def get_filtered_users_service(params: UserFilterSchema, user: Optional[User] = None):
    query = User.all().only(
        "id",
        "profile_sprite",
        "username",
        "country",
        "level",
        "total_pp",
    )

    if params.username and len(params.username) >= 2:
        query = query.filter(username__istartswith=params.username.strip())

    if params.friend_only:
        if not user:
            return {"total": 0, "items": []}
        
        friend_ids = await Friendship.filter(user_id=user.id).values_list("friend_id", flat=True)
        if not friend_ids:
            return {"total": 0, "items": []}
        
        query = query.filter(id__in=friend_ids)

    if params.my_country_only:
        if not user or not user.country:
            return {"total": 0, "items": []}
        
        query = query.filter(country=user.country)

    total = await query.count()

    # 정렬
    sort_map = {
        "username": "username",
        "rank": "-total_pp",
        "country": "country",
    }
    
    items = await query.order_by(
        sort_map.get(params.sort, "username")
    ).offset(params.offset).limit(params.size)

    if not items:
        return {"total": total, "items": []}

    user_ids = [item.id for item in items]
    rank_map = await ranking_service.get_ranks_batch(user_ids)

    results = []
    for item in items:
        user_data = {
            "id": item.id,
            "profile_sprite": item.profile_sprite,
            "username": item.username,
            "rank": rank_map.get(item.id) or 0,
            "country": item.country,
            "level": item.level,
        }
        results.append(user_data)

    return {
        "total": total,
        "items": results,
    }
