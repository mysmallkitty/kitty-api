import uvicorn
from tortoise import Tortoise

from fastapi import FastAPI

import settings
from app.user.router import router as user_router
from app.maps.router import router as maps_router
from app.records.router import router as records_router

MODELS = [
    "aerich.models",
    "app.user.models",
    "app.maps.models",
    "app.records.models",
]

ROUTERS = [
    user_router,
    maps_router,
    records_router,
]

async def lifespan(app: FastAPI):
    await Tortoise.init(db_url=settings.DB_URL, modules={"models": MODELS})
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
    uvicorn.run("main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG_MODE)

