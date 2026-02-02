from app.records.models import Record


async def recompute_total_pp(user_id: int) -> float:
    records = (
        await Record.filter(user_id=user_id, pp__not_isnull=True)
        .order_by("-pp")
        .limit(100)
    )
    total = 0.0
    weight = 1.0
    decay = 0.95
    for record in records:
        if record.pp is None:
            continue
        total += float(record.pp) * weight
        weight *= decay
    return total
