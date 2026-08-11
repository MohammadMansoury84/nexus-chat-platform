from uuid import UUID
from src.application.service.service_Interface.message_service import MessageService
from src.core.logger.CustomLogger import CustomLogger
from src.domain.entities.Message import Message
from src.domain.entities.MessageStatus import MessageStatus
from src.domain.entities.PrivateChat import PrivateChat
from src.domain.entities.PrivateChatMessage import PrivateChatMessage
from src.core.exceptions.PrivateChatNotFoundError import PrivateChatNotFoundError
from src.core.exceptions.UserNotFoundError import UserNotFoundError
from src.domain.repositories_Interface.private_chat_repositiry import PrivateChatRepository
from src.domain.repositories_Interface.user_repository import UserRepository
from src.application.DTO.private_message_dto.message_dto import MessageDTO
from src.application.DTO.private_message_dto.chat_message_dto import ChatMessageDTO

class MessageServiceImpl(MessageService):

    def __init__(self, user_repository: UserRepository,privateChat_repository :PrivateChatRepository) -> None:

        self._privateChat_repository= privateChat_repository
        self._user_repository = user_repository

        self.custome_logger = CustomLogger(self.__class__.__name__)



    def send_message(self, sender_id: UUID, receiver_id: UUID, content: str) -> MessageDTO:

        self.custome_logger.debug(
            "Attempting to send message",
            sender_id=sender_id,
            receiver_id=receiver_id,
            content=content,
        )

        sender = self._user_repository.get_by_id(sender_id)
        receiver = self._user_repository.get_by_id(receiver_id)

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
            self._privateChat_repository.add(private_chat=target_chat)

        message = PrivateChatMessage(
            sender_id=sender.id,
            receiver_id=receiver.id,
            content=content,
            status=MessageStatus.SENT,
        )

        target_chat.messages.append(message)

        self.custome_logger.info(
            "Message sent successfully", sender_id=sender_id, receiver_id=receiver_id
        )

        return MessageDTO(id=message.id,sender_id=sender_id, 
                        receiver_id=receiver.id,
                        content=message.content,
                        status=message.status
                    )
    
    def get_chat(self, user1_id: UUID, user2_id: UUID) -> list[ChatMessageDTO]:
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

            sender = self._user_repository.get_by_id(msg.sender_id)
            chat_result.append(
                ChatMessageDTO(
                    sender_id=sender.id,
                    username=sender.username,
                    content=msg.content,
                    status=msg.status)
            )
        return chat_result


        
    def delete_private_chat_history(self, user1_id: UUID, user2_id: UUID) -> bool:

        if self._user_repository.get_by_id(user1_id) is None:
            raise UserNotFoundError("user not found.")
        if self._user_repository.get_by_id(user2_id) is None:
            raise UserNotFoundError("user not found.")

        target_chat = self._get_private_chat(user1_id=user1_id, user2_id=user2_id)

        if target_chat is None:
            raise PrivateChatNotFoundError("You have no chat history with this person.")

        target_chat.messages.clear()

        return True


    def _get_private_chat(self, user1_id: UUID, user2_id: UUID) -> PrivateChat | None:
        self.custome_logger.debug(
            "Attempting to get private chat ", user1_id=user1_id, user2_id=user2_id
        )
        user = self._user_repository.get_by_id(user_id=user1_id)
        for chat in user.private_chats:
            is_user1_to_user2 = chat.user1_id == user1_id and chat.user2_id == user2_id
            is_user2_to_user1 = chat.user1_id == user2_id and chat.user2_id == user1_id

            if is_user1_to_user2 or is_user2_to_user1:
                return chat

        return None

    
