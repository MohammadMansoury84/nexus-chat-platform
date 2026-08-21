from uuid import UUID

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from src.domain.entities.Group import Group
from src.domain.repositories_Interface.group_repository import GroupRepository
from src.infrastructure.Brief.group.get_all_groups_for_show_users_brief import (
    GetAllGroupsForShowUsersBrief,
)
from src.infrastructure.Brief.group.get_group_by_id_brief import GetGroupByIdBrief
from src.infrastructure.Brief.group.group_chat_message_brief import GroupChatMessageBrief
from src.infrastructure.database.orm_models.group_members_model import GroupMembersModel
from src.infrastructure.database.orm_models.group_message_model import GroupMessageModel
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

    async def get_group_with_messages(self, group_id: UUID) -> list[GroupChatMessageBrief]:
        stmt = (
            select(GroupModel)
            .where(GroupModel.id == group_id)
            .options(selectinload(GroupModel.messages).joinedload(GroupMessageModel.sender))
        )

        result = await self._db.scalars(stmt)
        group_model = result.unique().first()

        if group_model is None or not group_model.messages:
            return []

        return [
            GroupChatMessageBrief(
                id=msg.id,
                group_id=msg.group_id,
                sender_id=msg.sender_id,
                sender_username=msg.sender.username,
                content=msg.content,
                created_at=msg.created_at,
            )
            for msg in group_model.messages
        ]

    async def get_all_groups_for_show_users(
        self, user_id: UUID
    ) -> list[GetAllGroupsForShowUsersBrief]:

        stmt = (
            select(GroupModel.id, GroupModel.name)
            .outerjoin(GroupMembersModel, GroupMembersModel.group_id == GroupModel.id)
            .where(
                or_(GroupMembersModel.user_id == user_id, GroupModel.creator_id == user_id)
            )
            .distinct()
        )

        result = await self._db.execute(stmt)
        rows = result.all()

        return [
            GetAllGroupsForShowUsersBrief(group_id=row.id, group_name=row.name)
            for row in rows
        ]
