from tortoise.expressions import F
from app.maps.models import Map
from app.records.models import Record, Stat
from app.records.pp.calculate_pp import calculate_pp
from app.records.redis_services import ranking_service
from app.user.models import User
from tortoise.transactions import in_transaction



class PPService:
    @staticmethod
    async def update_record_and_ranking(user_id: int, map_id: int, clear_time: int, deaths: int, current_pp: float):
        best_record = await Record.filter(
            user_id=user_id, 
            map_id=map_id
        ).select_for_update().first()
        
        old_pp = best_record.pp if best_record and best_record.pp else 0

        if best_record is None:
            await Record.create(
                user_id=user_id, map_id=map_id, pp=current_pp,
                clear_time=clear_time, deaths=deaths, replay_url=""
            )
            await PPService._update_ranking(user_id)
            
        elif current_pp > old_pp:
            best_record.pp = current_pp
            best_record.clear_time = clear_time
            best_record.deaths = deaths
            await best_record.save()
            
            await PPService._update_ranking(user_id)

    @staticmethod
    async def _update_ranking(user_id: int):
        new_total_pp = await PPService.recompute_total_pp(user_id)
        await User.filter(id=user_id).update(total_pp=new_total_pp)
        await ranking_service.update_user_pp(user_id, new_total_pp)

    @staticmethod
    async def recompute_total_pp(user_id: int) -> float:
        records = (
            await Record.filter(user_id=user_id, pp__not_isnull=True)
            .order_by("-pp")
            .limit(100)
        )
        total, weight = 0.0, 1.0
        for r in records:
            total += float(r.pp or 0) * weight
            weight *= 0.95
        return total

    @staticmethod
    def calculate_pp_for_clear(map_obj: Map, deaths: int, clear_time: int) -> float:
        if not map_obj.is_ranked: return 0.0
        class TempRecord:
            def __init__(self, d, t): self.deaths, self.clear_time = d, t
        return float(calculate_pp(map_obj, TempRecord(deaths, clear_time)))
    
pp_service = PPService()


class ClearsService:
    @staticmethod
    async def increment_global_clears(user_id: int, map_id: int):
        await User.filter(id=user_id).update(total_clears=F("total_clears") + 1)
        await Map.filter(id=map_id).update(total_clears=F("total_clears") + 1)
        
clear_service = ClearsService()
