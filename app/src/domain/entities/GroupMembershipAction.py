from enum import Enum


class GroupMembershipAction(str, Enum):
    GROUP_DELETED = "group_deleted"
    USER_LEFT = "user_left"
    USER_REMOVED = "user_removed"