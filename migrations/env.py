import asyncio
import sys
import os
from logging.config import fileConfig

from alembic import context
from sqlalchemy.ext.asyncio import create_async_engine, async_engine_from_config
from sqlalchemy import pool

# Добавляем путь к проекту
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Импортируем ваши модели
from src.database.database import Base
from src.publications.models import Publication
from src.categories.models import Category

target_metadata = Base.metadata

config = context.config
fileConfig(config.config_file_name)

def run_migrations_offline():
    context.configure(url=config.get_main_option("sqlalchemy.url"), target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()

def do_run_migrations(connection):
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()

async def run_migrations_online():
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())