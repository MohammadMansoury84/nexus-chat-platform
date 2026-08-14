
from uuid import UUID

from src.application.service.service_Interface.user_service import UserService
from src.application.DTO.user.user_dto import UserDTO
from src.core.exceptions.UserNotFoundError import UserNotFoundError
from src.domain.repositories_Interface.user_repository import UserRepository
from src.application.DTO.user.user_summary_dto import UserSummaryDTO


class UserServiceImpl(UserService):

    def __init__(self,user_repository : UserRepository):
        self._user_repository=user_repository

        
    def get_other_logged_in_users_for_show(
        self,
        current_user_id: UUID, 
    ) -> list[UserSummaryDTO]:
        return [
            UserSummaryDTO(id=user.id,email=user.email, username=user.username)
            for user in self._user_repository.list_all()
            if user.id in self._user_repository.get_logged_in_user_ids() and user.id != current_user_id
        ]

    def get_user_by_id(self, user_id: UUID) -> UserDTO | None:

        user = self._user_repository.get_by_id(user_id=user_id)
        if user is None:
            raise UserNotFoundError("User not found.")

        return UserDTO(
            id=user.id, 
            username=user.username,
            email=user.email
            )

    def get_all_users(self) -> list[UserSummaryDTO]:

        return [
            UserSummaryDTO(id=user.id,email=user.email, username=user.username)
            for user in self._user_repository.list_all()
        ]
