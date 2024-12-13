import os
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession


async_engine = None
AsyncSessionLocal = None


def init_db():
    global async_engine, AsyncSessionLocal
    if async_engine is None:
        async_engine = create_async_engine(
            os.getenv("DB_URL"), pool_size=10, max_overflow=0, pool_pre_ping=False, pool_recycle=1800
        )
    AsyncSessionLocal = sessionmaker(
        bind=async_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )


def get_db_engine():
    return async_engine


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session