
from abc import ABC, abstractmethod
from src.domain.entities.PrivateChat import PrivateChat


class PrivateChatRepository(ABC):

    @abstractmethod
    def add(self, private_chat: PrivateChat) -> PrivateChat:
        pass
