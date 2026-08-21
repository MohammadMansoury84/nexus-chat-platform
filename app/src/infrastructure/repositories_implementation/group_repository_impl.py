from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.domain.entities.Group import Group
from src.domain.repositories_Interface.group_repository import GroupRepository
from src.infrastructure.Brief.group.get_group_by_id_brief import GetGroupByIdBrief
from src.infrastructure.database.orm_models.group_model import GroupModel


class GroupRepositoryImpl(GroupRepository):
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def add(self, group: Group) -> Group:
        orm_group = GroupModel(
            id=group.id,
            name=group.name,
            creator_id=group.creator_id,
            created_at=group.created_at,
        )

        self._db.add(orm_group)

        return group

    async def get_by_id(self, group_id: UUID) -> GetGroupByIdBrief | None:

        stmt = select(GroupModel).where(GroupModel.id == group_id)
        result = await self._db.scalar(statement=stmt)
        if result is None:
            return None

        return GetGroupByIdBrief(
            group_id=result.id,
            group_name=result.name,
            creator_id=result.creator_id,
            created_at=result.created_at,
        )

    async def list_all(self) -> list[Group]:
        return self._groups

    async def remove_group(self, group: Group) -> bool:
        if group in self._groups:
            self._groups.remove(group)
            return True
        return False
