import asyncio
from uuid import UUID

from src.controllers.AuthController import AuthController
from src.controllers.GroupController import GroupController
from src.controllers.MessageController import MessageController
from src.entities.DTO.Request.AddUserToGroupRequest import AddUserToGroupRequest
from src.entities.DTO.Request.CreateGroupRequest import CreateGroupRequest
from src.entities.DTO.Request.DeleteGroupByIdRequest import DeleteGroupByIdRequest
from src.entities.DTO.Request.DeleteGroupChatHistoryRequest import (
    DeleteGroupChatHistoryRequest,
)
from src.entities.DTO.Request.DeletePrivateChatHistoryRequest import (
    DeletePrivateChatHistoryRequest,
)
from src.entities.DTO.Request.GetChatRequest import GetChatRequest
from src.entities.DTO.Request.GetGroupChatRequest import GetGroupChatRequest
from src.entities.DTO.Request.LoginRequest import LoginRequest
from src.entities.DTO.Request.RemoveUserFromGroupRequest import (
    RemoveUserFromGroupRequest,
)
from src.entities.DTO.Request.SendMessageTOGroupRequest import SendMessageToGroupRequest
from src.entities.DTO.Request.SendMessageToPrivateChatRequest import (
    SendMessageToPrivateChatRequest,
)
from src.entities.DTO.Request.ShowGroupMembersRequest import ShowGroupMembersRequest
from src.entities.DTO.Request.SignupRequest import SignupRequest
from src.entities.MessageStatus import MessageStatus
from src.ServerNetwork.ConnectionManagement import ConnectionManagement


class RequestHandler:
    def __init__(
        self,
        auth_controller: AuthController,
        message_controller: MessageController,
        group_controller: GroupController,
        connections_management: ConnectionManagement,
    ):
        self._auth_controller = auth_controller
        self._message_controller = message_controller
        self._group_controller = group_controller
        self._connectionsManagement = connections_management

    async def signup(self, data: dict, writer: asyncio.StreamWriter) -> dict:
        dto = SignupRequest(**data)

        user_id = self._auth_controller.signup(
            username=dto.username,
            email=dto.email,
            password=dto.password,
        )

        return {"user_id": str(user_id), "message": "User signed up successfully."}

    async def login(self, data: dict, writer: asyncio.StreamWriter) -> dict:
        current_user = self._connectionsManagement.get_logged_in_users(writer)

        if current_user is not None:
            return {"logged_in": False, "message": "You are already logged in."}

        dto = LoginRequest(**data)
        user = self._auth_controller.login(username=dto.username, password=dto.password)
        if not user:
            return {"logged_in": False, "message": "Username or password is wrong."}

        self._connectionsManagement.login(user_id=user.id, writer=writer)

        return {
            "logged_in": True,
            "user": {"id": str(user.id), "username": user.username},
        }

    async def logout(self, writer: asyncio.StreamWriter) -> dict:
        current_user_id = self._connectionsManagement.get_logged_in_user_id(writer)

        if current_user_id is None:
            return {
                "message": "You are not logged in.",
            }

        self._connectionsManagement.logout(writer=writer)
        return {"message": "Logged out."}

    async def get_all_users(
        self,
        data: dict,
        writer: asyncio.StreamWriter,
    ) -> dict:
        current_user_id = self._require_login(writer)

        logged_in_user_ids = self._connectionsManagement.get_logged_in_user_ids()

        users = self._auth_controller.get_other_logged_in_users_for_show(
            current_user_id=current_user_id,
            logged_in_user_ids=logged_in_user_ids,
        )

        if not users:
            return {
                "users": [],
                "message": "No other users are logged in.",
            }

        return {
            "users": users,
            "message": "Logged-in users retrieved successfully.",
        }

    async def send_private_message(
        self,
        data: dict,
        writer: asyncio.StreamWriter,
    ) -> dict:
        dto = SendMessageToPrivateChatRequest(**data)

        self._check_current_user(
            writer=writer,
            request_user_id=dto.sender_id,
        )

        message = self._message_controller.send_message(
            sender_id=dto.sender_id,
            receiver_id=dto.receiver_id,
            content=dto.message_content,
        )

        sender = self._auth_controller.get_user_by_id(dto.sender_id)

        delivered = await self._send_request(
            user_id=dto.receiver_id,
            message_type="event",
            event="private_message",
            date={
                "sender_id": str(dto.sender_id),
                "sender_username": (sender.username if sender else "Unknown"),
                "content": message.content,
            },
        )

        return {
            "message_id": str(message.id),
            "message": (
                "Message delivered." if delivered else "Message saved. User is offline."
            ),
            "delivered": MessageStatus.DELIVERED,
        }

    async def get_private_chat(self, data: dict, writer: asyncio.StreamWriter) -> dict:

        dto = GetChatRequest(
            user1_id=UUID(data["user1_id"]),
            user2_id=UUID(data["user2_id"]),
        )
        self._check_current_user(writer, dto.user1_id)
        chat = self._message_controller.get_chat(
            user1_id=dto.user1_id, user2_id=dto.user2_id
        )
        return {"chat": chat}

    async def create_group(self, data: dict, writer: asyncio.StreamWriter) -> dict:
        dto = CreateGroupRequest(
            group_name=data["group_name"],
            creator_id=UUID(data["creator_id"]),
        )
        self._check_current_user(writer, dto.creator_id)
        group_id = self._group_controller.create_group(
            name=dto.group_name, creator_id=dto.creator_id
        )
        return {"group_id": str(group_id), "message": "Group created."}

    async def get_all_groups(self, data: dict, writer: asyncio.StreamWriter) -> dict:
        user_id = self._require_login(writer=writer)
        return {"groups": self._group_controller.get_all_groups_for_show_users(user_id)}

    async def add_user_to_group(self, data: dict, writer: asyncio.StreamWriter) -> dict:
        dto = AddUserToGroupRequest(
            group_id=UUID(data["group_id"]),
            creator_id=UUID(data["creator_id"]),
            user_id=UUID(data["user_id"]),
        )
        self._check_current_user(writer, dto.creator_id)

        result = self._group_controller.add_user_to_group(
            group_id=dto.group_id,
            creator_id=dto.creator_id,
            user_id=dto.user_id,
        )

        group = self._group_controller.get_group_by_id(group_id=dto.group_id)

        await self._send_request(
            user_id=dto.user_id,
            message_type="event",
            event="added_to_group",
            date={
                "group_id": str(dto.group_id),
                "group_name": group.name,
            },
        )

        return {"message": result}

    async def send_group_message(self, data: dict, writer: asyncio.StreamWriter) -> dict:
        dto = SendMessageToGroupRequest(
            group_id=UUID(data["group_id"]),
            sender_id=UUID(data["sender_id"]),
            message_content=data["message_content"],
        )

        self._check_current_user(writer, dto.sender_id)

        message = self._group_controller.send_message_to_group(
            group_id=dto.group_id,
            sender_id=dto.sender_id,
            content=dto.message_content,
        )

        group = self._group_controller.get_group_by_id(group_id=dto.group_id)
        sender = self._auth_controller.get_user_by_id(user_id=dto.sender_id)

        if group is not None:
            for member in group.members:
                if member.id == dto.sender_id:
                    continue
                await self._send_request(
                    user_id=member.id,
                    message_type="event",
                    event="group_message",
                    date={
                        "group_id": str(dto.group_id),
                        "group_name": group.name,
                        "sender_username": sender.username if sender else "Unknown",
                        "content": message.content,
                    },
                )

        return {"message_id": str(message.id), "message": "Group message sent."}

    async def get_group_chat(self, data: dict, writer: asyncio.StreamWriter) -> dict:
        dto = GetGroupChatRequest(group_id=UUID(data["group_id"]))
        current_user = self._require_login(writer)
        group = self._group_controller.get_group_by_id(dto.group_id)
        is_member = group is not None and any(
            member.id == current_user for member in group.members
        )
        if not is_member:
            return {"chat": [], "message": "Group was not found or user is not a member."}

        return {"chat": self._group_controller.get_group_chat(dto.group_id)}

    async def delete_group_by_id(self, data: dict, writer: asyncio.StreamWriter) -> dict:

        current_user_id = self._connectionsManagement.get_logged_in_users(writer)

        dto = DeleteGroupByIdRequest(
            group_id=UUID(data["group_id"]),
        )

        group = self._group_controller.get_group_by_id(dto.group_id)

        if group is None:
            return {
                "message": "Group not found.",
                "deleted": False,
            }

        members = list(group.members)

        result = self._group_controller.delete_group_by_id(
            user_id=current_user_id,
            group_id=dto.group_id,
        )

        if result:
            for member in members:
                if member.id == current_user_id:
                    continue
                await self._send_request(
                    user_id=member.id,
                    message_type="event",
                    event="delete_group",
                    date={
                        "group_id": str(dto.group_id),
                        "group_name": group.name,
                        "content": f"Group {group.name} deleted successfully.",
                    },
                )

        return {
            "message": "Group deleted successfully.",
            "deleted": result,
        }

    async def leave_private_chat(self, data: dict, writer: asyncio.StreamWriter) -> dict:
        user_id = self._connectionsManagement.get_logged_in_users(writer=writer)

        other_user_id = UUID(data["other_user_id"])

        current_user = self._auth_controller.get_user_by_id(user_id=user_id)

        result = await self._send_request(
            user_id=other_user_id,
            message_type="event",
            event="exit_private_chat",
            date={
                "user_id": str(user_id),
                "username": (current_user.username if current_user else "Unknown"),
            },
        )
        return {
            "message": "Private chat closed.",
            "delivered": result,
        }

    async def leave_group_chat(self, data: dict, writer: asyncio.StreamWriter) -> dict:
        user_id = self._connectionsManagement.get_logged_in_users(writer=writer)
        user = self._auth_controller.get_user_by_id(user_id=user_id)

        group_id = UUID(data["group_id"])
        group = self._group_controller.get_group_by_id(group_id=group_id)
        members = group.members

        for member in members:
            if member.id == user_id:
                continue
            await self._send_request(
                user_id=member.id,
                message_type="event",
                event="exit_group_chat",
                date={
                    "user_id": str(user_id),
                    "username": user.username,
                    "group_id": group_id,
                    "group_name": group.name,
                },
            )

        return {
            "message": "group chat closed.",
        }

    async def show_group_members(self, data: dict, writer: asyncio.StreamWriter) -> dict:
        self._require_login(writer=writer)
        dto = ShowGroupMembersRequest(**data)
        return {
            "users": self._group_controller.show_group_member(
                user_id=dto.user_id, group_id=dto.group_id
            )
        }

    async def delete_privet_chat_history(
        self, data: dict, writer: asyncio.StreamWriter
    ) -> dict:
        self._require_login(writer=writer)
        dto = DeletePrivateChatHistoryRequest(**data)
        result = self._message_controller.delete_private_chat_history(
            user1_id=dto.user1_id, user2_id=dto.user2_id
        )
        if result:
            user = self._auth_controller.get_user_by_id(dto.user2_id)
            await self._send_request(
                user_id=dto.user2_id,
                message_type="event",
                event="delete_private_chat_history",
                date={"message": f"{user.username} deleted privet chat history "},
            )
            return {"data": "privet chat history deleted"}

        return {"data": "request faild"}

    async def delete_group_chat_history(
        self, data: dict, writer: asyncio.StreamWriter
    ) -> dict:
        self._require_login(writer=writer)
        dto = DeleteGroupChatHistoryRequest(**data)
        result = self._group_controller.delete_group_chat_history(
            user_id=dto.user_id, group_id=dto.group_id
        )
        if result:
            group = self._group_controller.get_group_by_id(dto.group_id)
            user = self._auth_controller.get_user_by_id(dto.user_id)
            for member in group.members:
                if member.id == dto.user_id:
                    continue
                await self._send_request(
                    user_id=member.id,
                    message_type="event",
                    event="delete_group_chat_history",
                    date={
                        "message": f"{user.username} deleted "
                        f"group '{group.name}' chat history"
                    },
                )
            return {"data": "group chat history deleted"}

        return {"data": "request faild"}

    async def remove_user_from_group(
        self,
        data: dict,
        writer: asyncio.StreamWriter,
    ) -> dict:

        admin_id = self._require_login(writer)

        dto = RemoveUserFromGroupRequest(**data)

        group = self._group_controller.get_group_by_id(dto.group_id)

        result = self._group_controller.remove_user_from_group(
            admin_id=admin_id,
            group_id=dto.group_id,
            user_id=dto.user_id,
        )

        admin = self._auth_controller.get_user_by_id(admin_id)

        admin_username = admin.username if admin else "Unknown"

        event_data = {
            "group_id": result["group_id"],
            "group_name": result["group_name"],
            "removed_user_id": result["removed_user_id"],
            "removed_username": result["removed_username"],
            "removed_by_id": str(admin_id),
            "removed_by_username": admin_username,
            "message": (
                f"{result['removed_username']} was removed "
                f"from group '{result['group_name']}'."
            ),
        }

        if group is not None:
            for member in group.members:
                if member.id in {
                    admin_id,
                    dto.user_id,
                }:
                    continue

                await self._send_request(
                    user_id=member.id,
                    message_type="event",
                    event="member_removed_from_group",
                    date=event_data,
                )

        await self._send_request(
            user_id=dto.user_id,
            message_type="event",
            event="member_removed_from_group",
            date=event_data,
        )

        return {
            "message": (f"{result['removed_username']} removed from group successfully."),
            "removed": True,
        }

    def _require_login(self, writer: asyncio.StreamWriter) -> UUID:
        user_id = self._connectionsManagement.get_logged_in_users(writer)
        if user_id is None:
            raise ValueError("Please login first.")
        return user_id

    def _check_current_user(
        self, writer: asyncio.StreamWriter, request_user_id: UUID
    ) -> None:
        current_user = self._require_login(writer)
        if current_user != request_user_id:
            raise ValueError("Request user does not match logged-in user.")

    async def _send_request(
        self, user_id: UUID, message_type: str, event: str, date: dict
    ) -> bool:
        return await self._connectionsManagement.send_to_user(
            user_id=user_id,
            message={"message_type": message_type, "event": event, "data": date},
        )
