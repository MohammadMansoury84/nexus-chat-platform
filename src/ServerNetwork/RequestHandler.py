import asyncio
from uuid import UUID

from src.controllers.AuthController import AuthController
from src.controllers.GroupController import GroupController
from src.controllers.MessageController import MessageController
from src.entities.DTO.Request.AddUserToGroupRequest import AddUserToGroupRequest
from src.entities.DTO.Request.CreateGroupRequest import CreateGroupRequest
from src.entities.DTO.Request.GetChatRequest import GetChatRequest
from src.entities.DTO.Request.GetGroupChatRequest import GetGroupChatRequest
from src.entities.DTO.Request.LoginRequest import LoginRequest
from src.entities.DTO.Request.SendMessageTOGroupRequest import SendMessageToGroupRequest
from src.entities.DTO.Request.SendMessageToPrivateChatRequest import (
    SendMessageToPrivateChatRequest,
)
from src.entities.DTO.Request.SignupRequest import SignupRequest
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
        dto = LoginRequest(**data)
        user = self._auth_controller.login(username=dto.userName, password=dto.password)
        if not user:
            return {"logged_in": False, "message": "Username or password is wrong."}

        self._connectionsManagement.login(user_id=user.id, writer=writer)

        return {
            "logged_in": True,
            "user": {"id": str(user.id), "username": user.username},
        }

    async def logout(self, writer: asyncio.StreamWriter) -> dict:
        self._connectionsManagement.logout(writer=writer)
        return {"message": "Logged out."}

    async def get_all_users(self) -> dict:
        return {"users": self._auth_controller.get_all_users_for_show_users()}

    async def send_private_message(
        self,
        data: dict,
        writer: asyncio.StreamWriter,
    ) -> dict:

        dto = SendMessageToPrivateChatRequest(
            sender_id=UUID(data["sender_id"]),
            receiver_id=UUID(data["receiver_id"]),
            message_content=data["message"],
        )

        self._check_current_user(writer, dto.sender_id)

        message = self._message_controller.send_message(
            sender_id=dto.sender_id,
            receiver_id=dto.receiver_id,
            content=dto.message_content,
        )

        sender = self._auth_controller.get_user_by_id(dto.sender_id)

        await self._connectionsManagement.send_to_user(
            dto.receiver_id,
            {
                "message_type": "event",
                "event": "private_message",
                "data": {
                    "sender_id": str(dto.sender_id),
                    "sender_username": sender.username if sender else "Unknown",
                    "content": message.content,
                },
            },
        )
        return {"message_id": str(message.id), "message": "Message sent."}

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

    async def get_all_groups(self) -> dict:
        return {"groups": self._group_controller.get_all_groups_for_show_users()}

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

        await self._connectionsManagement.send_to_user(
            dto.user_id,
            {
                "message_type": "event",
                "event": "added_to_group",
                "data": {"group_id": str(dto.group_id)},
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
                await self._connectionsManagement.send_to_user(
                    member.id,
                    {
                        "message_type": "event",
                        "event": "group_message",
                        "data": {
                            "group_id": str(dto.group_id),
                            "sender_username": sender.username if sender else "Unknown",
                            "content": message.content,
                        },
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
