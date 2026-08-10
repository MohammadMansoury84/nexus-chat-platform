from abc import ABC, abstractmethod
from uuid import UUID
from src.domain.entities.User import User
from src.application.DTO.user.user_dto import UserDTO
from src.application.DTO.user.user_summary_dto import UserSummaryDTO

class AuthService(ABC):


    @abstractmethod
    def signup(self, username: str, email: str, password: str) -> UserDTO:
        pass

    @abstractmethod
    def login(self, username: str, password: str) -> UserDTO:
        pass
        
    @abstractmethod
    def get_user_by_id(self, user_id: UUID) -> UserDTO:
        pass

    @abstractmethod
    def get_other_logged_in_users_for_show(
        self,
        current_user_id: UUID,
        logged_in_user_ids: set[UUID],
    ) -> list[UserSummaryDTO]:
        pass

    @abstractmethod
    def get_all_users(self) -> list[UserDTO]:
        pass




    




