from unittest.mock import create_autospec

import pytest

from src.entities.Group import Group
from src.entities.User import User
from src.repository.GroupRepository import GroupRepository
from src.repository.UserRepository import UserRepository


@pytest.fixture
def user_repository():
    return create_autospec(
        UserRepository,
        instance=True,
    )


@pytest.fixture
def group_repository():
    return create_autospec(
        GroupRepository,
        instance=True,
    )
