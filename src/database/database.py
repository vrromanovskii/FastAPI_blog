import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set")

engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

Base = declarative_base()

# Импортируем модели, чтобы Base.metadata знал о них
from src.auth.models import User
from src.publications.models import Publication, DeletedPublication
from src.categories.models import Category

async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session