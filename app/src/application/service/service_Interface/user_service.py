from abc import ABC, abstractmethod
from uuid import UUID

from src.application.DTO.user.user_dto import UserDTO
from src.application.DTO.user.user_summary_dto import UserSummaryDTO

class UserService(ABC):


    @abstractmethod
    def get_other_logged_in_users_for_show(
        self,
        current_user_id: UUID,
        logged_in_user_ids: set[UUID],
    ) -> list[UserSummaryDTO]:
        pass


    @abstractmethod
    def get_user_by_id(self, user_id: UUID) -> UserDTO | None:
        pass


    @abstractmethod
    def get_all_users(self) -> list[UserSummaryDTO]:
        pass


    



