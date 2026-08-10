from abc import ABC, abstractmethod
from src.domain.entities.GroupMessage import GroupMessage

class GroupMessageRepository(ABC):
    
    @abstractmethod
    def add(self, group_message: GroupMessage) -> GroupMessage:
        pass