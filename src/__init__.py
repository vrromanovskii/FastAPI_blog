from fastapi import FastAPI
from src.categories.routes import cat_router
from src.publications.routes import publ_router
from contextlib import asynccontextmanager
from src.database.database import engine, Base
from src.auth.routes import auth_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Создаём таблицы при старте приложения
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Очистка ресурсов при остановке
    await engine.dispose()

app = FastAPI(lifespan=lifespan)

app.include_router(auth_router)
app.include_router(cat_router, prefix="/category")
app.include_router(publ_router, prefix="/publication")