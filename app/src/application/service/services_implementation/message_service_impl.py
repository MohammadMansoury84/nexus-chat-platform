from uuid import UUID

from src.application.DTO.private_message_dto.chat_message_dto import ChatMessageDTO
from src.application.DTO.private_message_dto.message_dto import MessageDTO
from src.application.service.service_Interface.message_service import MessageService
from src.core.exceptions.AuthorizationError import AuthorizationError
from src.core.exceptions.PrivateChatNotFoundError import PrivateChatNotFoundError
from src.core.exceptions.UserNotFoundError import UserNotFoundError
from src.core.logger.CustomLogger import CustomLogger
from src.domain.entities.MessageStatus import MessageStatus
from src.domain.entities.PrivateChat import PrivateChat
from src.domain.entities.PrivateChatMessage import PrivateChatMessage
from src.domain.repositories_Interface.message_repository import MassageRepository
from src.domain.repositories_Interface.private_chat_repositiry import PrivateChatRepository
from src.domain.repositories_Interface.redis_online_user_repository import (
    RedisOnlineUserRepository,
)
from src.domain.repositories_Interface.user_repository import UserRepository


class MessageServiceImpl(MessageService):
    def __init__(
        self,
        user_repository: UserRepository,
        privateChat_repository: PrivateChatRepository,
        online_user_repository: RedisOnlineUserRepository,
        message_repository: MassageRepository,
    ) -> None:

        self._private_chat_repository = privateChat_repository
        self._user_repository = user_repository
        self._online_user_repository = online_user_repository
        self._message_repository = message_repository

        self.custome_logger = CustomLogger(self.__class__.__name__)

    async def send_message(
        self, sender_id: UUID, receiver_id: UUID, content: str
    ) -> MessageDTO:

        self.custome_logger.debug(
            "Attempting to send message",
            sender_id=sender_id,
            receiver_id=receiver_id,
            content=content,
        )

        sender = await self._user_repository.get_by_id(sender_id)
        receiver = await self._user_repository.get_by_id(receiver_id)

        if sender is None:
            raise UserNotFoundError("Sender not found.")
        if receiver is None:
            raise UserNotFoundError("Receiver not found.")

        is_online = await self._online_user_repository.is_user_logged_in(
            user_id=receiver_id
        )
        if not is_online:
            raise AuthorizationError("Receiver is not logged in.")

        target_chat_id = await self._private_chat_repository.get_private_chat_by_user_ids(
            user1_id=sender_id, user2_id=receiver_id
        )

        if target_chat_id is None:
            target_chat = PrivateChat(user1_id=sender_id, user2_id=receiver_id)
            self.custome_logger.info(
                "PrivateChat create successfully",
                sender_id=sender_id,
                receiver_id=receiver_id,
            )
            target_chat_id = target_chat.id
            await self._private_chat_repository.add(private_chat=target_chat)

        message = PrivateChatMessage(
            chat_id=target_chat_id,
            sender_id=sender.id,
            receiver_id=receiver.id,
            content=content,
            status=MessageStatus.SENT,
        )

        await self._message_repository.add(message=message)

        self.custome_logger.info(
            "Message sent successfully", sender_id=sender_id, receiver_id=receiver_id
        )

        return MessageDTO(
            id=message.id,
            sender_username=sender.username,
            receiver_username=receiver.username,
            content=message.content,
            status=message.status,
        )

    async def get_chat(self, user1_id: UUID, user2_id: UUID) -> list[ChatMessageDTO]:
        self.custome_logger.debug(
            "Attempting to get chat", user1_id=user1_id, user2_id=user2_id
        )

        messages = await self._private_chat_repository.get_private_chat_with_messages(
            user1_id=user1_id, user2_id=user2_id
        )

        if not messages:
            return []

        unread_message_ids = [
            msg.id
            for msg in messages
            if msg.sender_id != user1_id and msg.status != MessageStatus.READ
        ]

        if unread_message_ids:
            await self._private_chat_repository.mark_messages_as_read(unread_message_ids)

            for msg in messages:
                if msg.id in unread_message_ids:
                    msg.status = MessageStatus.READ

        return [
            ChatMessageDTO(
                sender_id=msg.sender_id,
                username=msg.sender_username,
                content=msg.content,
                status=msg.status,
                timestamp=msg.timestamp,
            )
            for msg in messages
        ]

    async def delete_private_chat_history(self, user1_id: UUID, user2_id: UUID) -> bool:

        if await self._user_repository.get_by_id(user1_id) is None:
            raise UserNotFoundError("user not found.")
        if await self._user_repository.get_by_id(user2_id) is None:
            raise UserNotFoundError("user not found.")

        chat_id = await self._private_chat_repository.get_private_chat_by_user_ids(
            user1_id, user2_id
        )

        if chat_id is None:
            raise PrivateChatNotFoundError("You have no chat history with this person.")

        await self._message_repository.delete_messages_by_chat_id(chat_id=chat_id)

        return True

    async def mark_chat_as_read(self, reader_id: UUID, chat_partner_id: UUID) -> list[UUID]:

        messages = await self._private_chat_repository.get_private_chat_with_messages(
            user1_id=reader_id, user2_id=chat_partner_id
        )

        unread_messages = [
            message
            for message in messages
            if message.sender_id == chat_partner_id and message.status != MessageStatus.READ
        ]

        if not unread_messages:
            return []

        unread_message_ids = [msg.id for msg in unread_messages]
        await self._private_chat_repository.mark_messages_as_read(unread_message_ids)

        return unread_message_ids
