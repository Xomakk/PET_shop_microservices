from typing import List, TypeVar, Generic, Type
from sqlalchemy.ext.asyncio import AsyncSession
from auth.models import User
from sqlalchemy import select, update, delete
from database import BaseModel

T = TypeVar("T", bound=BaseModel)


class BaseDAO(Generic[T]):
    model: Type[T] = None

    def __init__(self, session: AsyncSession):
        self._session = session

        if self.model is None:
            raise ValueError("Model not implemented.")

    async def find_one_or_none(self, data_id: int) -> User | None:
        stmt = select(self.model).filter(self.model.id == data_id)

        query = await self._session.execute(stmt)
        return query.scalar_one_or_none()

    async def find_many(self, **filter_by) -> list[User]:
        stmt = select(self.model).filter_by(**filter_by)

        query = await self._session.execute(stmt)
        return query.scalars().all()

    async def update_one(self, data_id: int, data: dict) -> User:
        stmt = update(self.model).filter(self.model.id == data_id).values(**data)

        await self._session.execute(stmt)

    async def delete_one(self, data_id: int) -> None:
        stmt = delete(self.model).filter(self.model.id == data_id)

        await self._session.execute(stmt)
