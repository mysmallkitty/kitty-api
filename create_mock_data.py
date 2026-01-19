import asyncio
import random

from dotenv import load_dotenv
from tortoise import Tortoise

import settings
from app.maps.models import Map
from app.user.models import Friendship, Roles, User

load_dotenv()


async def create_mock_data():
    import os

    await Tortoise.init(config=settings.TORTOISE_ORM)
    await Tortoise.generate_schemas()

    print("🗑️  기존 데이터 삭제 중...")
    await Friendship.all().delete()

    await Map.all().delete()
    await User.all().delete()

    print("👥 유저 생성 중...")
    users = []

    admin = User(
        username="admin",
        email="admin@example.com",
        profile_img_url="https://i.pravatar.cc/150?img=1",
        role=Roles.ADMIN.value,
        level=99,
        exp=999999,
        country="KR",
        skill_level=10.0,
    )
    admin.set_password("admin123")
    await admin.save()
    users.append(admin)

    mod = User(
        username="moderator",
        email="mod@example.com",
        profile_img_url="https://i.pravatar.cc/150?img=2",
        role=Roles.MOD.value,
        level=50,
        exp=50000,
        country="KR",
        skill_level=8.5,
    )
    mod.set_password("mod123")
    await mod.save()
    users.append(mod)

    # 일반 유저 20명
    for i in range(3, 23):
        user = User(
            username=f"user{i}",
            email=f"user{i}@example.com",
            profile_img_url=f"https://i.pravatar.cc/150?img={i}",
            role=Roles.USER.value,
            level=random.randint(1, 30),
            exp=random.randint(0, 10000),
            country=random.choice(["KR", "US", "JP", "CN", "UK"]),
            total_deaths=random.randint(100, 10000),
            total_attempts=random.randint(200, 15000),
            total_clears=random.randint(50, 5000),
            skill_level=round(random.uniform(0.5, 7.0), 1),
        )
        user.set_password(f"password{i}")
        await user.save()
        users.append(user)

    print(f"✅ {len(users)}명의 유저 생성 완료")

    print("🗺️  맵 생성 중...")
    map_titles = [
        "초보자를 위한 연습맵",
        "점프 마스터",
        "스피드런 챌린지",
        "익스트림 난이도",
        "퍼즐 맵",
        "보스 러시",
        "타이밍 훈련장",
        "정밀 컨트롤",
        "엔듀런스 테스트",
        "크리에이티브 파쿠르",
        "레이싱 트랙",
        "서바이벌 모드",
        "트릭샷 연습",
        "클래식 맵",
        "실험적 디자인",
    ]

    maps = []
    for i, title in enumerate(map_titles, 1):
        creator = random.choice(users)
        map_obj = await Map.create(
            title=title,
            detail=f"{title}에 대한 설명입니다. 난이도와 플레이 스타일에 맞춰 제작되었습니다.",
            level=round(random.uniform(1.0, 10.0), 1),
            creator=creator,
            is_ranked=random.choice([True, False]),
            is_wip=random.choice([True, False]),
            map_url=f"https://storage.example.com/maps/map_{i}.dat",
            thumbnail_url=f"https://picsum.photos/800/600?random={i}",
            total_deaths=random.randint(500, 50000),
            total_attempts=random.randint(1000, 100000),
            total_clears=random.randint(100, 20000),
            loved_count=random.randint(0, 500),
            download_count=random.randint(10, 5000),
        )
        maps.append(map_obj)

    print(f"✅ {len(maps)}개의 맵 생성 완료")

    print("🤝 친구 관계 생성 중...")
    friendships = 0
    for user in users[:10]:  # 처음 10명만
        friends_to_add = random.sample(
            [u for u in users if u.id != user.id], k=random.randint(2, 5)
        )
        for friend in friends_to_add:
            await Friendship.create(user=user, friend=friend)
            friendships += 1

    print(f"✅ {friendships}개의 친구 관계 생성 완료")

    print("\n📊 생성된 데이터 요약:")
    print(f"  - 유저: {len(users)}명")
    print(f"  - 맵: {len(maps)}개")
    print(f"  - 친구 관계: {friendships}개")
    print("\n✨ 목 데이터 생성 완료!")

    await Tortoise.close_connections()


if __name__ == "__main__":
    asyncio.run(create_mock_data())
