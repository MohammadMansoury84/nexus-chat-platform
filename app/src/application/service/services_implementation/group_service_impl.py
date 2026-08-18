from uuid import UUID

from src.application.DTO.group.group_chat_message_dto import GroupChatMessageDTO
from src.application.DTO.group.group_member_dto import GroupMemberDTO
from src.application.DTO.group.group_membership_action_dto import GroupMembershipActionDTO
from src.application.DTO.group.group_message_dto import GroupMessageDTO
from src.application.DTO.group.group_summary_dto import GroupSummaryDTO
from src.application.DTO.group.grtoup_dto import GroupDTO
from src.application.service.service_Interface.group_service import GroupService
from src.core.exceptions.AuthorizationError import AuthorizationError
from src.core.exceptions.GroupNotFoundError import GroupNotFoundError
from src.core.exceptions.UserAlreadyInGroupError import UserAlreadyInGroupError
from src.core.exceptions.UserNotFoundError import UserNotFoundError
from src.core.exceptions.UserNotInGroupError import UserNotInGroupError
from src.core.logger.CustomLogger import CustomLogger
from src.domain.entities.Group import Group
from src.domain.entities.GroupMembershipAction import GroupMembershipAction
from src.domain.entities.GroupMessage import GroupMessage
from src.domain.entities.MessageStatus import MessageStatus
from src.domain.repositories_Interface.group_message_repository import (
    GroupMessageRepository,
)
from src.domain.repositories_Interface.group_repository import GroupRepository
from src.domain.repositories_Interface.user_repository import UserRepository


class GroupServiceImpl(GroupService):
    def __init__(
        self,
        user_repository: UserRepository,
        group_repository: GroupRepository,
        group_message_repository: GroupMessageRepository,
    ) -> None:
        self._user_repository = user_repository
        self._group_repository = group_repository
        self._group_message_repository = group_message_repository

        self.custome_logger = CustomLogger(self.__class__.__name__)

    def create_group(self, name: str, creator_id: UUID) -> GroupDTO:

        self.custome_logger.debug(
            "Attempting to create group", name=name, creator_id=creator_id
        )

        group = Group(name=name, creator_id=creator_id)
        target_user = self._user_repository.get_by_id(user_id=creator_id)

        if target_user is None:
            self.custome_logger.warning("User not found", user_id=creator_id)
            raise UserNotFoundError("User not found.")

        target_user.groups_created.append(group)
        target_user.joined_groups.append(group)
        group.members.append(target_user)
        self._group_repository.add(group)

        self.custome_logger.info(
            "Group created successfully",
            group_id=group.id,
            name=name,
            creator_id=creator_id,
        )

        return GroupDTO(
            group_id=group.id, group_name=group.name, creator_id=group.creator_id
        )

    def add_user_to_group(self, group_id: UUID, creator_id: UUID, user_id: UUID) -> bool:

        self.custome_logger.debug(
            "Attempting to add user to group",
            group_id=group_id,
            creator_id=creator_id,
            user_id=user_id,
        )

        group = self._group_repository.get_by_id(group_id=group_id)
        user = self._user_repository.get_by_id(user_id)

        if user is None:
            self.custome_logger.warning("User not found", user_id=user_id)

            raise UserNotFoundError("User not found.")

        if group is None:
            self.custome_logger.warning("Group not found", group_id=group_id)

            raise GroupNotFoundError("Group not found.")

        if creator_id != group.creator_id:
            self.custome_logger.warning(
                "User is not the creator of the group",
                creator_id=creator_id,
                group_id=group_id,
            )
            raise AuthorizationError("only the creator can add members to the group.")

        if not self._user_repository.is_user_logged_in(user_id=user_id):
            raise AuthorizationError("User must be logged in before joining the group.")

        if user in group.members:
            self.custome_logger.warning(
                "User is already in the group", user_id=user_id, group_id=group_id
            )

            raise UserAlreadyInGroupError("User is already in the group.")

        group.members.append(user)
        user.joined_groups.append(group)

        self.custome_logger.info(
            "User added to group successfully", user_id=user_id, group_id=group_id
        )
        return True

    def send_message_to_group(
        self, group_id: UUID, sender_id: UUID, content: str
    ) -> GroupMessageDTO:

        self.custome_logger.debug(
            "Attempting to send message to group",
            group_id=group_id,
            sender_id=sender_id,
            content=content,
        )

        group = self._group_repository.get_by_id(group_id=group_id)
        sender = self._user_repository.get_by_id(sender_id)

        if group is None:
            self.custome_logger.warning("Group not found", group_id=group_id)
            raise GroupNotFoundError("Group not found.")

        if sender is None:
            self.custome_logger.warning("Sender not found", sender_id=sender_id)
            raise UserNotFoundError("User not found.")

        if sender not in group.members:
            self.custome_logger.warning(
                "Sender is not a member of the group",
                sender_id=sender_id,
                group_id=group_id,
            )
            raise UserNotInGroupError("User is not a member of the group.")

        message = GroupMessage(
            sender_id=sender.id,
            group_id=group.id,
            content=content,
            status=MessageStatus.SENT,
        )
        group.messages.append(message)
        self._group_message_repository.add(message)

        self.custome_logger.info(
            "Message sent to group successfully",
            group_id=group_id,
            sender_id=sender_id,
            content=content,
        )

        return GroupMessageDTO(
            sender_id=sender.id,
            group_id=group.id,
            content=message.content,
            status=message.status,
        )

    def get_group_chat(
        self, group_id: UUID, sender_id: UUID
    ) -> list[GroupChatMessageDTO] | None:

        self.custome_logger.debug("Attempting to get group chat", group_id=group_id)

        group = self._group_repository.get_by_id(group_id=group_id)
        sender = self._user_repository.get_by_id(sender_id)

        if group is None:
            self.custome_logger.error("Group not found", group_id=group_id)
            raise GroupNotFoundError("Group not found.")
        if sender is None:
            self.custome_logger.warning(
                "User not found",
                sender_id=sender_id,
            )
            raise UserNotFoundError("User not found.")

        if sender not in group.members:
            self.custome_logger.warning(
                "Sender is not a member of the group",
                sender_id=sender_id,
                group_id=group_id,
            )
            raise UserNotInGroupError("User is not a member of the group.")

        chat = []
        for msg in group.messages:
            sender = self._user_repository.get_by_id(msg.sender_id)

            chat.append(
                GroupChatMessageDTO(
                    sender_id=sender.id, username=sender.username, content=msg.content
                )
            )

        self.custome_logger.info("Group chat retrieved successfully", group_id=group_id)
        return chat

    def get_group_by_id(self, group_id: UUID) -> GroupDTO:
        group = self._group_repository.get_by_id(group_id=group_id)

        if group is None:
            raise GroupNotFoundError("Group not found.")

        return GroupDTO(
            group_id=group.id, group_name=group.name, creator_id=group.creator_id
        )

    def get_all_groups_for_show_users(self, user_id: UUID) -> list[GroupSummaryDTO]:
        return [
            GroupSummaryDTO(group_id=group.id, group_name=group.name)
            for group in self._get_joined_groups_and_groups_created_users(user_id=user_id)
        ]

    def get_all_groups(self) -> list[GroupSummaryDTO]:
        return [
            GroupSummaryDTO(group_id=group.id, group_name=group.name)
            for group in self._group_repository.list_all()
        ]

    def delete_group_by_id(self, user_id: UUID, group_id: UUID) -> bool:

        group = self._group_repository.get_by_id(group_id=group_id)

        if group is None:
            self.custome_logger.error("Group not found", group_id=group_id)
            raise GroupNotFoundError("Group not found.")

        if user_id == group.creator_id:
            group.messages.clear()
            members = group.members

            for member in members:
                if group in member.groups_created:
                    member.groups_created.remove(group)

                if group in member.joined_groups:
                    member.joined_groups.remove(group)

            group.members.clear()
            is_remove = self._group_repository.remove_group(group=group)
            if is_remove:
                self.custome_logger.info(
                    "Group deleted successfully",
                    group_id=str(group_id),
                )
                self.custome_logger.info("Group deleted successfully", group_id=group_id)
                return True

        raise AuthorizationError("only admin can delete group")

    def show_group_member(self, user_id: UUID, group_id: UUID) -> list[GroupMemberDTO]:
        group = self._group_repository.get_by_id(group_id=group_id)

        if group is None:
            self.custome_logger.error("Group not found", group_id=group_id)
            raise GroupNotFoundError("Group not found.")

        is_member = any(member.id == user_id for member in group.members)

        if not is_member:
            self.custome_logger.error(
                "Only group members can see group members.", user_id=user_id
            )
            raise AuthorizationError("Only group members can see group members.")

        self.custome_logger.info("show Group members", group_id=group_id)
        return [
            GroupMemberDTO(id=member.id, username=member.username)
            for member in group.members
        ]

    def delete_group_chat_history(self, user_id: UUID, group_id: UUID) -> bool:
        group = self._group_repository.get_by_id(group_id=group_id)

        if group is None:
            self.custome_logger.error("Group not found", group_id=group_id)
            raise GroupNotFoundError("Group not found.")

        if group.creator_id != user_id:
            self.custome_logger.error(
                "Only Admin can delete group chat history", group_id=group_id
            )
            raise AuthorizationError("Only Admin can delete group chat history")

        is_member = any(member.id == user_id for member in group.members)

        if not is_member:
            raise AuthorizationError("Only group members can see group members.")

        self.custome_logger.info(
            "Group chat history deleted successfully", group_id=group_id
        )

        group.messages.clear()

        return True

    def remove_user_from_group(
        self,
        admin_id: UUID,
        group_id: UUID,
        user_id: UUID,
    ) -> GroupMembershipActionDTO:

        group = self._group_repository.get_by_id(group_id=group_id)

        if group is None:
            raise GroupNotFoundError("Group not found.")

        target_user = self._user_repository.get_by_id(user_id=user_id)

        if target_user is None:
            raise UserNotFoundError("User not found.")

        target_member = next(
            (member for member in group.members if member.id == user_id),
            None,
        )

        if target_member is None:
            raise UserNotInGroupError("User is not a member of this group.")

        if admin_id == user_id:
            if group.creator_id == user_id:
                self.delete_group_by_id(
                    user_id=user_id,
                    group_id=group_id,
                )

                return GroupMembershipActionDTO(
                    action=GroupMembershipAction.GROUP_DELETED,
                    group_id=group.id,
                    group_name=group.name,
                    user_id=target_member.id,
                    username=target_member.username,
                )

            group.members.remove(target_member)

            if group in target_user.joined_groups:
                target_user.joined_groups.remove(group)

            return GroupMembershipActionDTO(
                action=GroupMembershipAction.USER_LEFT,
                group_name=group.name,
                group_id=group.id,
                user_id=target_member.id,
                username=target_member.username,
            )

        if group.creator_id != admin_id:
            raise AuthorizationError("Only group creator can remove members.")

        if group.creator_id == user_id:
            raise AuthorizationError("Group creator cannot be removed.")

        group.members.remove(target_member)

        if group in target_user.joined_groups:
            target_user.joined_groups.remove(group)

        return GroupMembershipActionDTO(
            action=GroupMembershipAction.USER_REMOVED,
            group_name=group.name,
            group_id=group.id,
            user_id=target_member.id,
            username=target_member.username,
        )

    def _get_joined_groups_and_groups_created_users(self, user_id: UUID) -> list[Group]:

        user = self._user_repository.get_by_id(user_id=user_id)
        list1 = user.groups_created
        list2 = user.joined_groups

        merge_list = []
        seen_ids = set()

        for group in list1 + list2:
            if group.id not in seen_ids:
                merge_list.append(group)
                seen_ids.add(group.id)

        return merge_list
