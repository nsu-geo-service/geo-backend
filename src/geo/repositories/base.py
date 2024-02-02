import uuid
from typing import Generic, Type, TypeVar, Optional

from sqlalchemy import update, delete, func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

T = TypeVar('T')


class BaseRepository(Generic[T]):
    table: Type[T]

    def __init__(self, session: AsyncSession):
        self._session = session

    async def create(self, commit: bool = True, **kwargs) -> T:
        """
        Создает запись в БД

        :param commit: автоматический коммит
        :param kwargs:
        :return:
        """
        model = self.table(**kwargs)
        self._session.add(model)
        if commit:
            await self._session.commit()
        return model

    async def get(self, **kwargs) -> Optional[T]:
        """
        Получает запись

        :param kwargs:
        :return:
        """
        return (await self._session.execute(select(self.table).filter_by(**kwargs))).scalars().first()

    async def get_all(
            self,
            limit: int = None,
            offset: int = None,
            order_by: str = "id",
            **kwargs
    ) -> list[Optional[T]]:
        """
        Получает все записи

        :param limit: лимит 100
        :param offset: смещение 0
        :param kwargs: filter by
        :param order_by: сортировка
        :return:
        """
        stmt = (
            select(self.table)
            .filter_by(**kwargs)
            .order_by(text(order_by))
        )

        if limit:
            stmt = stmt.limit(limit)
        if offset:
            stmt = stmt.offset(offset)

        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def update(self, id: uuid.UUID, commit: bool = True, **kwargs) -> None:
        """
        Обновляет запись

        :param id:
        :param commit: автоматический коммит
        :param kwargs:
        :return:
        """
        if kwargs:
            await self._session.execute(update(self.table).where(self.table.id == id).values(**kwargs))
            if commit:
                await self._session.commit()

    async def delete(self, id: uuid.UUID, commit: bool = True) -> None:
        """
        Удаляет запись

        :param id:
        :param commit: автоматический коммит
        :return:
        """
        await self._session.execute(delete(self.table).where(self.table.id == id))
        if commit:
            await self._session.commit()

    async def count(self, **kwargs) -> int:
        """
        Возвращает количество записей

        :param kwargs:
        :return:
        """
        return (await self._session.execute(select(func.count()).select_from(self.table).filter_by(**kwargs))).scalar()

    @property
    def session(self) -> AsyncSession:
        return self._session
