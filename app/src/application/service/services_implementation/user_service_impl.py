from uuid import UUID

from src.application.DTO.user.user_dto import UserDTO
from src.application.DTO.user.user_summary_dto import UserSummaryDTO
from src.application.service.service_Interface.user_service import UserService
from src.core.exceptions.UserNotFoundError import UserNotFoundError
from src.domain.repositories_Interface.redis_online_user_repository import (
    RedisOnlineUserRepository,
)
from src.domain.repositories_Interface.user_repository import UserRepository


class UserServiceImpl(UserService):
    def __init__(
        self,
        user_repository: UserRepository,
        online_user_repository: RedisOnlineUserRepository,
    ):
        self._user_repository = user_repository
        self._online_user_repository = online_user_repository

    async def get_other_logged_in_users_for_show(
        self,
        current_user_id: UUID,
    ) -> list[UserSummaryDTO]:

        online_uuids = await self._online_user_repository.get_online_user_ids()

        online_uuids.discard(current_user_id)

        if not online_uuids:
            return []

        users = await self._user_repository.get_by_ids(list(online_uuids))

        return [
            UserSummaryDTO(id=user.id, email=user.email, username=user.username)
            for user in users
        ]

    async def get_user_by_id(self, user_id: UUID) -> UserDTO | None:

        user = await self._user_repository.get_by_id(user_id=user_id)
        if user is None:
            raise UserNotFoundError("User not found.")

        return UserDTO(id=user.id, username=user.username, email=user.email)

    async def get_all_users(self) -> list[UserSummaryDTO]:

        return [
            UserSummaryDTO(id=user.id, email=user.email, username=user.username)
            for user in await self._user_repository.list_all()
        ]
