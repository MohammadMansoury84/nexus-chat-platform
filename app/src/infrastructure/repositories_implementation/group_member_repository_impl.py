from uuid import UUID

from sqlalchemy import and_, delete, exists, select
from sqlalchemy.ext.asyncio import AsyncSession
from src.domain.repositories_Interface.group_member_repository import GroupMemberRepository
from src.infrastructure.database.orm_models.group_members_model import GroupMembersModel


class GroupMemberRepositoryImpl(GroupMemberRepository):
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def add_member(self, group_id: UUID, user_id: UUID, role: str = "member") -> None:
        member_orm = GroupMembersModel(group_id=group_id, user_id=user_id, role=role)
        self._db.add(member_orm)

    async def is_user_in_group(self, user_id: UUID, group_id: UUID) -> bool:

        stmt = select(
            exists().where(
                GroupMembersModel.user_id == user_id, GroupMembersModel.group_id == group_id
            )
        )
        result = await self._db.scalar(stmt)
        return bool(result)

    async def remove_user(self, group_id: UUID, user_id: UUID) -> None:
        stmt = delete(GroupMembersModel).where(
            and_(
                GroupMembersModel.group_id == group_id, GroupMembersModel.user_id == user_id
            )
        )

        await self._db.execute(statement=stmt)
