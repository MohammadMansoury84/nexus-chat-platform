from enum import StrEnum


class RequestType(StrEnum):
    SINGUP = "signup"
    LOGIN = "login"
    GET_USER_BY_ID = "get_user_by_id"
    GET_ALL_USERS_FOR_SHOW_USERS = "get_all_users_for_show_users"
    GET_ALL_USERS = "get_all_users"
    CREATE_GROUP = "create_group"
    ADD_USER_TO_GROUP = "add_user_to_group"
    SEND_MESSAGE_TO_GROUP = "send_message_to_group"
    GET_GROUP_CHAT = "get_group_chat"
    GET_GROUP_BY_ID = "get_group_by_id"
    GET_ALL_GROUPS_FOR_SHOW_USERS = "get_all_groups_for_show_users"
    GET_ALL_GROUPS = "get_all_groups"
    SEND_MESSAGE = "send_message"
    GET_CHAT = "get_chat"
