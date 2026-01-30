import uvicorn
from fastapi import FastAPI, Request
from tortoise import Tortoise
from fastapi.middleware.cors import CORSMiddleware
import settings
from app.maps.router import router as maps_router
from app.records.router import router as records_router
from app.user.router import router as user_router
from app.play.router import router as play_router
from app.admin.main import setup_admin



ROUTERS = [
    user_router,
    maps_router,
    records_router,
    play_router,
]


async def lifespan(app: FastAPI):
    await Tortoise.init(config=settings.TORTOISE_ORM)
    await setup_admin(app)
    yield
    await Tortoise.close_connections()


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
for router in ROUTERS:
    app.include_router(router)


# 헬스체크 엔드포인트
@app.get("/health")
async def health_check(request: Request):
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run(
        "main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG_MODE
    )
