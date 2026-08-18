from abc import ABC, abstractmethod
from uuid import UUID

from src.application.DTO.group.group_chat_message_dto import GroupChatMessageDTO
from src.application.DTO.group.group_member_dto import GroupMemberDTO
from src.application.DTO.group.group_membership_action_dto import GroupMembershipActionDTO
from src.application.DTO.group.group_message_dto import GroupMessageDTO
from src.application.DTO.group.group_summary_dto import GroupSummaryDTO
from src.application.DTO.group.grtoup_dto import GroupDTO


class GroupService(ABC):
    @abstractmethod
    def create_group(self, name: str, creator_id: UUID) -> GroupDTO:
        pass

    @abstractmethod
    def add_user_to_group(self, group_id: UUID, creator_id: UUID, user_id: UUID) -> bool:
        pass

    @abstractmethod
    def send_message_to_group(
        self, group_id: UUID, sender_id: UUID, content: str
    ) -> GroupMessageDTO:
        pass

    @abstractmethod
    def get_group_chat(
        self, group_id: UUID, sender_id: UUID
    ) -> list[GroupChatMessageDTO] | None:
        pass

    @abstractmethod
    def get_group_by_id(self, group_id: UUID) -> GroupDTO:
        pass

    @abstractmethod
    def get_all_groups_for_show_users(self, user_id: UUID) -> list[GroupSummaryDTO]:
        pass

    @abstractmethod
    def get_all_groups(self) -> list[GroupSummaryDTO]:
        pass

    @abstractmethod
    def delete_group_by_id(self, user_id: UUID, group_id: UUID) -> bool:
        pass

    @abstractmethod
    def show_group_member(self, user_id: UUID, group_id: UUID) -> list[GroupMemberDTO]:
        pass

    @abstractmethod
    def delete_group_chat_history(self, user_id: UUID, group_id: UUID) -> bool:
        pass

    @abstractmethod
    def remove_user_from_group(
        self,
        admin_id: UUID,
        group_id: UUID,
        user_id: UUID,
    ) -> GroupMembershipActionDTO:
        pass
