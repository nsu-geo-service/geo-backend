from uuid import UUID

from sqlalchemy import text, select
from sqlalchemy.orm import subqueryload

from geo.models import tables
from geo.repositories.base import BaseRepository


class DetectionRepo(BaseRepository[tables.Detection]):
    table = tables.Detection

    async def get_all_by_task(
            self,
            task_id: UUID,
            limit: int = None,
            offset: int = None,
            order_by: str = None,
            **kwargs
    ) -> list[tables.Detection]:
        """
        Получает все записи

        :param task_id: идентификатор задачи
        :param limit: лимит 100
        :param offset: смещение 0
        :param kwargs: filter by
        :param order_by: сортировка
        :return:
        """
        stmt = (
            select(self.table)
            .options(
                subqueryload(self.table.event),
                subqueryload(self.table.station),
            )
            .where(self.table.event.has(task_id=task_id))
        )
        if limit:
            stmt = stmt.limit(limit)
        if offset:
            stmt = stmt.offset(offset)
        if order_by:
            stmt = stmt.order_by(text(order_by))

        result = await self._session.execute(stmt)
        return result.scalars().all()
