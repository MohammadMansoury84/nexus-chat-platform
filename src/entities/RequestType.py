from enum import StrEnum


class RequestType(StrEnum):
    SINGUP = "signup"
    LOGIN = "login"
    LOGOUT = "logout"
    GET_ALL_USERS_FOR_SHOW_USERS = "get_all_users_for_show_users"
    SEND_PRIVATE_MESSAGE = "send_private_message"
    GET_PRIVATE_CHAT = "get_private_chat"
    CREATE_GROUP = "create_group"
    GET_ALL_GROUPS_FOR_SHOW_USERS = "get_all_groups_for_show_users"
    ADD_USER_TO_GROUP = "add_user_to_group"
    SEND_MESSAGE_TO_GROUP = "send_message_to_group"
    GET_GROUP_CHAT = "get_group_chat"
    DELETE_GROUP_BY_ID = "delete_group_by_id"
    LEAVE_PRIVATE_CHAT = "leave_private_chat"
    LEAVE_GROUP_CHAT = "leave_group_chat"
    SHOW_GROUP_MEMBER = "show_group_members"
    DELETE_PRIVATE_CHAT_History = "delete_private_chat_history"
    DELETE_GROUP_CHAT_History = "delete_group_chat_history"
