from typing import Any

import pytest

from src.entities.Group import Group
from src.entities.MessageStatus import MessageStatus
from src.entities.User import User
from src.Exceptions.DuplicateUsernameError import DuplicateUsernameError
from src.repository.GroupRepository import GroupRepository
from src.repository.UserRepository import UserRepository
from src.service.AuthService import AuthService
from src.service.GroupService import GroupService
from src.service.MessageService import MessageService


def test_signup_raises_duplicate_username_when_username_exists(
    user_repository: UserRepository | Any,
) -> None:
    existing_user = User(
        username="alice",
        email="old@test.com",
        password="123456",  # noqa: S106
    )

    user_repository.list_all.return_value = [existing_user]
    auth_service = AuthService(user_repository=user_repository)
    with pytest.raises(
        DuplicateUsernameError,
        match="Username already exists",
    ):
        auth_service.signup(
            username="alice",
            email="new@test.com",
            password="654321",  # noqa: S106
        )

    user_repository.add.assert_not_called()


def test_login_returns_user_when_credentials_are_correct(
    user_repository: UserRepository | Any,
) -> None:
    existing_user = User(
        username="alice",
        email="alice@test.com",
        password="123456",  # noqa: S106
    )

    user_repository.list_all.return_value = [existing_user]

    auth_service = AuthService(user_repository=user_repository)

    result = auth_service.login(
        username="alice",
        password="123456",  # noqa: S106
    )

    assert result is existing_user

    assert result.username == "alice"
    assert result.email == "alice@test.com"

    user_repository.list_all.assert_called_once_with()


def test_send_message_creates_new_private_chat_and_message(
    user_repository: UserRepository | Any,
) -> None:
    sender = User(
        username="alice",
        email="alice@test.com",
        password="123456",  # noqa: S106
    )

    receiver = User(
        username="bob12",
        email="bob@test.com",
        password="123456",  # noqa: S106
    )

    def get_user_by_id(user_id: Any) -> User | None:
        if user_id == sender.id:
            return sender

        if user_id == receiver.id:
            return receiver

        return None

    user_repository.get_by_id.side_effect = get_user_by_id

    message_service = MessageService(user_repository=user_repository)

    message = message_service.send_message(
        sender_id=sender.id,
        receiver_id=receiver.id,
        content="Hello Bob",
    )

    assert message.sender_id == sender.id
    assert message.receiver_id == receiver.id

    assert message.content == "Hello Bob"

    assert message.status == MessageStatus.SENT

    assert len(sender.private_chats) == 1
    assert len(receiver.private_chats) == 1

    private_chat = sender.private_chats[0]

    assert private_chat is receiver.private_chats[0]

    assert len(private_chat.messages) == 1

    assert private_chat.messages[0] is message


def test_send_message_to_group_adds_message_when_sender_is_member(
    user_repository: UserRepository | Any,
    group_repository: GroupRepository | Any,
) -> None:
    sender = User(
        username="alice",
        email="alice@test.com",
        password="123456",  # noqa: S106
    )

    group = Group(
        name="Test Group",
        creator_id=sender.id,
    )

    group.members.append(sender)

    group_repository.get_by_id.return_value = group
    user_repository.get_by_id.return_value = sender

    group_service = GroupService(
        user_repository=user_repository,
        group_repository=group_repository,
    )

    message = group_service.send_message_to_group(
        group_id=group.id,
        sender_id=sender.id,
        content="Hello Group",
    )

    assert message.sender_id == sender.id
    assert message.group_id == group.id

    assert message.content == "Hello Group"

    assert message.status == MessageStatus.SENT

    assert len(group.messages) == 1

    assert group.messages[0] is message

    group_repository.get_by_id.assert_called_once_with(group_id=group.id)

    user_repository.get_by_id.assert_called_once_with(sender.id)
