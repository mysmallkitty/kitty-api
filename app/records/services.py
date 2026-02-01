from tortoise.expressions import F
from app.maps.models import Map
from app.records.models import Record, Stat
from app.records.pp.calculate_pp import calculate_pp
from app.records.redis_services import ranking_service
from app.user.models import User
from tortoise.transactions import in_transaction



class ResultService:
    async def process_record(self, record_id: int):
        record = await Record.get(id=record_id).prefetch_related("map")

        pp = None
        if record.map.is_ranked:
            pp = calculate_pp(record.map, record)

        rank_update = None

        async with in_transaction():
            if pp is not None:
                record.pp = pp
                await record.save()

            stat = await Stat.get(
                user_id=record.user_id,
                map_id=record.map_id
            ).prefetch_related("best_pp_record", "best_time_record")

            dirty = False

            if record.map.is_ranked:
                old_pp = stat.best_pp_record.pp if stat.best_pp_record else 0

                if record.pp and record.pp > old_pp:
                    stat.best_pp_record = record
                    dirty = True

                    diff = record.pp - old_pp
                    await User.filter(id=record.user_id).update(
                        total_pp=F("total_pp") + diff
                    )

                    rank_update = (await User.get(id=record.user_id)).total_pp

            old_time = stat.best_time_record.clear_time if stat.best_time_record else None
            if old_time is None or record.clear_time < old_time:
                stat.best_time_record = record
                dirty = True

            if dirty:
                await stat.save()

        if rank_update is not None:
            await ranking_service.update_user_pp(record.user_id, rank_update)


result_service = ResultService()


class ClearsService:

    @staticmethod
    async def mark_first_clear(user_id: int, map_id: int):
        updated = await Stat.filter(
            user_id=user_id,
            map_id=map_id,
            is_cleared=False
        ).update(is_cleared=True)

        if updated:
            await User.filter(id=user_id).update(
                total_clears=F("total_clears") + 1
            )
            await Map.filter(id=map_id).update(
                total_clears=F("total_clears") + 1
            )
clear_service = ClearsService()