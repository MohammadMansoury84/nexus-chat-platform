from uuid import UUID

from src.entities.Group import Group
from src.entities.Message import Message
from src.service.GroupService import GroupService


class GroupController:
    def __init__(self, group_service: GroupService) -> None:
        self._group_service = group_service

    def create_group(self, name: str, creator_id: UUID) -> UUID:
        return self._group_service.create_group(name=name, creator_id=creator_id)

    def add_user_to_group(self, group_id: UUID, creator_id: UUID, user_id: UUID) -> str:

        return self._group_service.add_user_to_group(
            group_id=group_id, creator_id=creator_id, user_id=user_id
        )

    def send_message_to_group(
        self, group_id: UUID, sender_id: UUID, content: str
    ) -> Message:
        return self._group_service.send_message_to_group(
            group_id=group_id, sender_id=sender_id, content=content
        )

    def get_group_chat(self, group_id: UUID) -> list[dict] | None:
        return self._group_service.get_group_chat(group_id=group_id)

    def get_group_by_id(self, group_id: UUID) -> Group | None:
        return self._group_service.get_group_by_id(group_id=group_id)

    def get_all_groups_for_show_users(self, user_id: UUID) -> list[dict]:
        return self._group_service.get_all_groups_for_show_users(user_id=user_id)

    def get_all_groups(self) -> list[Group]:
        return self._group_service.get_all_groups()

    def delete_group_by_id(self, user_id: UUID, group_id: UUID) -> bool:
        return self._group_service.delete_group_by_id(user_id=user_id, group_id=group_id)

    def show_group_member(self, user_id: UUID, group_id: UUID):
        return self._group_service.show_group_member(user_id=user_id, group_id=group_id)

    def delete_group_chat_history(self, user_id: UUID, group_id: UUID):

        return self._group_service.delete_group_chat_history(
            user_id=user_id, group_id=group_id
        )

    def remove_user_from_group(self, admin_id: UUID, group_id: UUID, user_id: UUID) -> dict:
        return self._group_service.remove_user_from_group(
            admin_id=admin_id,
            group_id=group_id,
            user_id=user_id,
        )
