from abc import ABC, abstractmethod

from src.application.DTO.user.token_dto import TokenDTO
from src.application.DTO.user.user_dto import UserDTO


class AuthService(ABC):
    @abstractmethod
    async def signup(self, username: str, email: str, password: str) -> UserDTO:
        pass

    @abstractmethod
    async def login(self, username: str, password: str) -> TokenDTO:
        pass
