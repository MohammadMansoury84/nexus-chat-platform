from src.domain.entities.PrivateChat import PrivateChat
from src.domain.repositories_Interface.private_chat_repositiry import PrivateChatRepository


class PrivateChatRepositoryImpl(PrivateChatRepository):
    def __init__(self) -> None:
        self._privateChats: list[PrivateChat] = []

    def add(self, private_chat: PrivateChat) -> PrivateChat:
        self._privateChats.append(private_chat)
        return private_chat
