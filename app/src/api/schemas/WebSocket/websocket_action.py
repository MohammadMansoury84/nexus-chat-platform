from enum import StrEnum


class WebSocketAction(StrEnum):
    SEND_PRIVATE_MESSAGE = "send_private_message"
    SEND_GROUP_MESSAGE = "send_group_message"
