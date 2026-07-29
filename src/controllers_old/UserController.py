from uuid import UUID

from src.core.CustomeLogger import CustomLogger
from src.entities.Group import Group
from src.entities.Message import Message
from src.entities.MessageStatus import MessageStatus
from src.entities.PrivateChat import PrivateChat
from src.entities.User import User
from src.Exceptions import (
    AuthorizationError,
    DuplicateEmailError,
    DuplicateUsernameError,
    GroupNotFoundError,
    UserAlreadyInGroupError,
    UserNotFoundError,
)


class UserController:
    def __init__(self) -> None:

        self.users: list[User] = []
        self.groups: list[Group] = []

        self.custome_logger = CustomLogger("UserController")

    def signup(self, username: str, email: str, password: str) -> UUID | None:

        self.custome_logger.debug(
            "Attempting to sign up user", username=username, email=email, password=password
        )

        if any(user.username == username for user in self.users):
            self.custome_logger.warning("Username already exists", username=username)

            raise DuplicateUsernameError("Username already exists.")

        if any(user.email == email for user in self.users):
            self.custome_logger.warning("Email already exists", email=email)

            raise DuplicateEmailError("Email already exists.")

        user = User(username=username, email=email, password=password)

        self.users.append(user)

        self.custome_logger.info("User created", username=username, email=email)

        return user.id

    def login(self, username: str, password: str) -> User | None:

        self.custome_logger.debug(
            "Attempting to log in user", username=username, password=password
        )

        for user in self.users:
            if user.username == username and user.password == password:
                self.custome_logger.info("User logged in successfully", username=username)

                return user

        self.custome_logger.error("Failed to log in user", username=username)

        return None

    def send_message(self, sender_id: UUID, receiver_id: UUID, content: str):
        self.custome_logger.debug(
            "Attempting to send message",
            sender_id=sender_id,
            receiver_id=receiver_id,
            content=content,
        )

        sender = self._get_user_by_id(sender_id)
        receiver = self._get_user_by_id(receiver_id)

        if sender is None:
            raise UserNotFoundError("Sender not found.")
        if receiver is None:
            raise UserNotFoundError("Receiver not found.")

        target_chat = self._get_private_chat(sender_id, receiver_id)

        if target_chat is None:
            target_chat = PrivateChat(user1_id=sender_id, user2_id=receiver_id)
            self.custome_logger.info(
                "PrivateChat create successfully",
                sender_id=sender_id,
                receiver_id=receiver_id,
            )
            receiver.private_chats.append(target_chat)
            sender.private_chats.append(target_chat)

        message = Message(
            sender_id=sender.id,
            receiver_id=receiver.id,
            content=content,
            status=MessageStatus.SENT,
        )

        target_chat.messages.append(message)

        self.custome_logger.info(
            "Message sent successfully", sender_id=sender_id, receiver_id=receiver_id
        )
        return message

    def get_chat(self, user1_id: UUID, user2_id: UUID) -> list[dict]:
        self.custome_logger.debug(
            "Attempting to get chat", user1_id=user1_id, user2_id=user2_id
        )

        target_chat = self._get_private_chat(user1_id, user2_id)

        if target_chat is None:
            self.custome_logger.warning("No chat history found")
            return []

        chat_result = []
        for msg in target_chat.messages:
            if msg.receiver_id == user1_id and msg.status != MessageStatus.READ:
                msg.status = MessageStatus.READ

            sender = self._get_user_by_id(msg.sender_id)
            chat_result.append(
                {
                    "username": sender.username if sender else "Unknown",
                    "message": msg.content,
                }
            )

        return chat_result

    def create_group(self, name: str, creator_id: UUID):

        self.custome_logger.debug(
            "Attempting to create group", name=name, creator_id=creator_id
        )

        group = Group(name=name, creator_id=creator_id)
        target_user = self._get_user_by_id(user_id=creator_id)

        if target_user is None:
            self.custome_logger.warning("User not found", user_id=creator_id)
            raise UserNotFoundError(f"User {creator_id} not found.")

        target_user.groups_created.append(group)
        target_user.joined_groups.append(group)
        group.members.append(target_user)
        self.groups.append(group)

        self.custome_logger.info(
            "Group created successfully",
            group_id=group.id,
            name=name,
            creator_id=creator_id,
        )

        return group.id

    def add_user_to_group(self, group_id: UUID, creator_id: UUID, user_id: UUID):

        self.custome_logger.debug(
            "Attempting to add user to group",
            group_id=group_id,
            creator_id=creator_id,
            user_id=user_id,
        )

        group = self._get_group_by_id(group_id=group_id)
        user = self._get_user_by_id(user_id)

        if user is None:
            self.custome_logger.warning("User not found", user_id=user_id)

            raise UserNotFoundError(f"User {user_id} not found.")

        if group is None:
            self.custome_logger.warning("Group not found", group_id=group_id)

            raise GroupNotFoundError(f"Group {group_id} not found.")

        if creator_id != group.creator_id:
            self.custome_logger.warning(
                "User is not the creator of the group",
                creator_id=creator_id,
                group_id=group_id,
            )
            raise AuthorizationError(
                f"User {creator_id} is not the creator of the group.only the creator can add members to the group."
            )

        if user in group.members:
            self.custome_logger.warning(
                "User is already in the group", user_id=user_id, group_id=group_id
            )

            raise UserAlreadyInGroupError(f"User {user.username} is already in the group.")

        group.members.append(user)
        user.joined_groups.append(group)

        self.custome_logger.info(
            "User added to group successfully", user_id=user_id, group_id=group_id
        )
        return f"User {user.username} added to group {group.name}."

    def send_message_to_group(self, group_id: UUID, sender_id: UUID, content: str):

        self.custome_logger.debug(
            "Attempting to send message to group",
            group_id=group_id,
            sender_id=sender_id,
            content=content,
        )

        group = self._get_group_by_id(group_id=group_id)
        sender = self._get_user_by_id(sender_id)

        if group is None:
            self.custome_logger.warning("Group not found", group_id=group_id)
            raise GroupNotFoundError(f"Group {group_id} not found.")

        if sender is None:
            self.custome_logger.warning("Sender not found", sender_id=sender_id)
            raise UserNotFoundError(f"User {sender_id} not found.")

        if sender not in group.members:
            self.custome_logger.warning(
                "Sender is not a member of the group",
                sender_id=sender_id,
                group_id=group_id,
            )
            raise UserNotFoundError(f"User {sender_id} is not a member of the group.")

        message = Message(
            sender_id=sender.id,
            group_id=group.id,
            content=content,
            status=MessageStatus.SENT,
        )
        group.messages.append(message)

        self.custome_logger.info(
            "Message sent to group successfully",
            group_id=group_id,
            sender_id=sender_id,
            content=content,
        )

        return message

    def get_group_chat(self, group_id: UUID):

        self.custome_logger.debug("Attempting to get group chat", group_id=group_id)

        group = self._get_group_by_id(group_id=group_id)

        if group is None:
            self.custome_logger.error("Group not found", group_id=group_id)
            raise GroupNotFoundError(f"Group {group_id} not found.")

        chat = []
        if group.messages:
            for msg in group.messages:
                sender = self._get_user_by_id(msg.sender_id)

                chat.append({"username": sender.username, "message": msg.content})

            self.custome_logger.info("Group chat retrieved successfully", group_id=group_id)
            return chat
        return None

    def _get_user_by_id(self, user_id: UUID) -> User | None:
        self.custome_logger.debug("Attempting to get user by ID", user_id=user_id)

        for user in self.users:
            if user.id == user_id:
                return user

        return None

    def _get_group_by_id(self, group_id: UUID) -> Group | None:

        self.custome_logger.debug("Attempting to get group by ID", group_id=group_id)

        for group in self.groups:
            if group.id == group_id:
                return group

        return None

    def get_all_users(self):
        self.custome_logger.debug("Attempting to get all users")
        user_list = []
        for user in self.users:
            user_list.append(f"User ID: {user.id}, Username: {user.username}")
        return user_list

    def get_all_groups(self):
        self.custome_logger.debug("Attempting to get all groups")
        group_list = []
        for group in self.groups:
            group_list.append(f"Group ID: {group.id}, Group Name: {group.name}")
        return group_list

    def _get_private_chat(self, user1_id: UUID, user2_id: UUID) -> PrivateChat | None:
        self.custome_logger.debug(
            "Attempting to get private chat ", user1_id=user1_id, user2_id=user2_id
        )
        user = self._get_user_by_id(user_id=user1_id)
        for chat in user.private_chats:
            is_user1_to_user2 = chat.user1_id == user1_id and chat.user2_id == user2_id
            is_user2_to_user1 = chat.user1_id == user2_id and chat.user2_id == user1_id

            if is_user1_to_user2 or is_user2_to_user1:
                return chat

        return None
