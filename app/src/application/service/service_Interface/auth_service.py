from abc import ABC, abstractmethod
from uuid import UUID

from src.application.DTO.user.user_dto import UserDTO
from src.application.DTO.user.user_summary_dto import UserSummaryDTO
from src.application.DTO.user.token_dto import TokenDTO


class AuthService(ABC):
    @abstractmethod
    def signup(self, username: str, email: str, password: str) -> UserDTO:
        pass

    @abstractmethod
    def login(self, username: str, password: str) -> TokenDTO:
        pass


