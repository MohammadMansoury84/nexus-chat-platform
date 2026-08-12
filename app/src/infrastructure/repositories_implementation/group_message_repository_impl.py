from src.domain.entities.GroupMessage import GroupMessage
from src.domain.repositories_Interface.group_message_repository import (
    GroupMessageRepository,
)


class GroupMessageRepositoryImpl(GroupMessageRepository):
    def __init__(self) -> None:
        self._group_messages: list[GroupMessage] = []

    def add(self, group_message: GroupMessage) -> GroupMessage:
        self._group_messages.append(group_message)
        return group_message
