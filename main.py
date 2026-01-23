import uvicorn
from fastapi import FastAPI
from tortoise import Tortoise

import settings
from app.maps.router import router as maps_router
from app.records.router import router as records_router
from app.user.router import router as user_router
from app.play.router import router as play_router


ROUTERS = [
    user_router,
    maps_router,
    records_router,
    play_router,
]


async def lifespan(app: FastAPI):
    await Tortoise.init(config=settings.TORTOISE_ORM)
    yield
    await Tortoise.close_connections()


app = FastAPI(lifespan=lifespan)

# 라우터 등록
for router in ROUTERS:
    app.include_router(router)


# 헬스체크 엔드포인트
@app.route("/health")
async def health_check():
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run(
        "main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG_MODE
    )
