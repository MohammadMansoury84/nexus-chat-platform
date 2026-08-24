from enum import StrEnum


class GroupMembershipAction(StrEnum):
    GROUP_DELETED = "group_deleted"
    USER_LEFT = "user_left"
    USER_REMOVED = "user_removed"
    GROUP_CHAT_DELETED = "group_chat_deleted"
