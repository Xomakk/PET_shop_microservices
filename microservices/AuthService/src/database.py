from datetime import datetime
from typing import Annotated, AsyncGenerator
import aioredis
from fastapi import Depends
from sqlalchemy import Integer, func
from sqlalchemy.orm import DeclarativeBase, declared_attr, Mapped, mapped_column
from sqlalchemy.ext.asyncio import (
    AsyncAttrs,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from config import settings

DATABASE_URL = settings.get_db_url()
REDIS_URL = settings.get_redis_url()

engine = create_async_engine(url=DATABASE_URL, echo=settings.DEV_MODE, pool_recycle=850)
async_session_maker = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

redis = aioredis.from_url(REDIS_URL)


class BaseModel(AsyncAttrs, DeclarativeBase):
    __abstract__ = True

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), onupdate=func.now()
    )

    @declared_attr.directive
    def __tablename__(cls) -> str:
        return cls.__name__.lower() + "s"


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


SessionDep = Annotated[AsyncSession, Depends(get_async_session)]
