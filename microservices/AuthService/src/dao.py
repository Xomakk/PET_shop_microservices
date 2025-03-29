from typing import TypeVar, Generic, Type
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, insert
from database import BaseModel

T = TypeVar("T", bound=BaseModel)


class BaseDAO(Generic[T]):
    model: Type[T] = None

    def __init__(self, session: AsyncSession):
        self._session = session

        if self.model is None:
            raise ValueError("Model not implemented.")

    async def create(self, data: dict):
        stmt = insert(self.model).values(data)
        await self._session.execute(stmt)

    async def find_one_or_none(self, data_id: int):
        stmt = select(self.model).filter(self.model.id == data_id)
        query = await self._session.execute(stmt)
        return query.scalar_one_or_none()

    async def find_many(self, **filter_by):
        stmt = select(self.model).filter_by(**filter_by)
        query = await self._session.execute(stmt)
        return query.scalars().all()

    async def update_one(self, data_id: int, data: dict):
        stmt = update(self.model).filter(self.model.id == data_id).values(**data)
        await self._session.execute(stmt)

    async def delete_one(self, data_id: int):
        stmt = delete(self.model).filter(self.model.id == data_id)
        await self._session.execute(stmt)
