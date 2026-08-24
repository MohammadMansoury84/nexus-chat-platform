from enum import StrEnum


class WebSocketAction(StrEnum):
    SEND_PRIVATE_MESSAGE = "send_private_message"
    SEND_GROUP_MESSAGE = "send_group_message"
    GROUP_MESSAGE = "group_message"
    GROUP_MEMBER_ADDED = "group_member_added"
    GROUP_MEMBER_REMOVED = "group_member_removed"
    GROUP_MEMBER_LEFT = "group_member_left"
    GROUP_DELETED = "group_deleted"
    GROUP_CHAT_DELETED = "group_chat_deleted"
