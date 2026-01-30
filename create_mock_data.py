import asyncio
import random
from datetime import datetime, timedelta

from dotenv import load_dotenv
from tortoise import Tortoise

import settings
from app.maps.models import Map
from app.user.models import Friendship, Roles, User
from app.records.models import Record  # 👈 Record 모델 임포트 추가
from app.records.models import Record, Stat

load_dotenv()


async def create_mock_data():
    await Tortoise.init(config=settings.TORTOISE_ORM)
    await Tortoise.generate_schemas()

    print("🗑️  기존 데이터 삭제 중...")
    await Friendship.all().delete()
    await Record.all().delete()  # 👈 추가
    await Stat.all().delete()  # 👈 추가
    await Map.all().delete()
    await User.all().delete()

    print("👥 유저 생성 중...")
    users = []
    # (관리자, 모더레이터 및 일반 유저 생성 로직은 동일하므로 중략...)
    # [생략된 유저 생성 코드...]
    admin = User(
        username="admin",
        email="admin@example.com",
        role=Roles.ADMIN.value,
        country="KR",
    )
    admin.set_password("admin123")
    await admin.save()
    users.append(admin)

    for i in range(2, 30):  # 유저를 30명 정도로 늘려 리더보드를 풍성하게 함
        user = User(
            username=f"user{i}",
            email=f"user{i}@example.com",
            country=random.choice(["KR", "US", "JP", "CN", "UK"]),
            role=Roles.USER.value,
        )
        user.set_password(f"password{i}")
        await user.save()
        users.append(user)

    print("🗺️  맵 생성 중...")
    map_titles = [
        "초보자를 위한 연습맵",
        "점프 마스터",
        "스피드런 챌린지",
        "익스트림 난이도",
        "퍼즐 맵",
    ]  # 예시
    maps = []
    for i, title in enumerate(map_titles, 1):
        creator = random.choice(users)
        map_obj = await Map.create(
            title=title,
            detail=f"{title} 설명",
            level=round(random.uniform(1.0, 10.0), 1),
            creator=creator,
            is_ranked=True,
            map_url=f"https://storage.example.com/map_{i}.dat",
        )
        maps.append(map_obj)

    print("🏆 플레이 기록(Records) 생성 중...")

    # 1. 특정 맵(1번 맵)에 집중적으로 기록 추가 (리더보드용)
    first_map = maps[0]
    print(f"📍 '{first_map.title}'에 리더보드 데이터 생성 중...")
    print("🏆 플레이 기록(Records) 및 통계(Stats) 생성 중...")

    first_map = maps[0]  # '초보자를 위한 연습맵'

    # 1번 맵에 25개의 기록 생성 (상위 20명 리더보드 테스트용)
    for i in range(25):
        player = random.choice(users)
        deaths = random.randint(0, 50)

        # Record 생성 시 replay_url을 반드시 포함 (에러 방지)
        await Record.create(
            map=first_map,
            user=player,
            deaths=deaths,
            clear_time=random.randint(10000, 300000),
            replay_url=f"https://storage.example.com/replays/rec_{i}.rpy",  # 필수 값
            created_at=datetime.now() - timedelta(days=random.randint(0, 7)),
        )

        # Stat 생성 (유저별 맵 통계)
        # unique_together 컬럼 체크를 위해 get_or_create 사용 권장
        stat_obj, created = await Stat.get_or_create(
            map=first_map,
            user=player,
            defaults={
                "deaths": deaths,
                "attempts": random.randint(1, 10),
                "is_cleared": True,
                "is_loved": random.choice([True, False]),
            },
        )

    print(f"✅ '{first_map.title}'에 25개의 기록 생성 완료")

    # 나머지 맵에도 랜덤하게 기록 추가
    for m in maps[1:]:
        for _ in range(random.randint(2, 5)):
            await Record.create(
                map=m,
                user=random.choice(users),
                deaths=random.randint(0, 100),
                clear_time=random.randint(20000, 500000),
                replay_url="https://storage.example.com/replays/default.rpy",  # 필수 값
            )
    # ==========================================


if __name__ == "__main__":
    asyncio.run(create_mock_data())
