from sqlalchemy.ext.asyncio import AsyncSession
from auth.models import User
from sqlalchemy import select, update, delete


class UserDAO:
    model = User

    def __init__(self, session: AsyncSession):
        self._session = session

    async def find_one_or_none(self, id: int) -> User | None:
        stmt = select(self.model).filter(self.model.id == id)

        query = await self._session.execute(stmt)
        return query.scalar_one_or_none()

    async def find_many(self, **filter_by) -> list[User]:
        stmt = select(self.model).filter_by(**filter_by)

        query = await self._session.execute(stmt)
        return query.scalars().all()

    async def update_one(self, id: int, data: dict) -> User:
        stmt = update(self.model).filter(self.model.id == id).values(**data)

        await self._session.execute(stmt)

    async def delete_one(self, id: int) -> None:
        stmt = delete(self.model).filter(self.model.id == id)

        await self._session.execute(stmt)
