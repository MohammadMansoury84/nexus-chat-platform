from abc import ABC, abstractmethod
from uuid import UUID


class TokenService(ABC):
    @abstractmethod
    def create_access_token(self, user_id: UUID) -> str:
        pass

    @abstractmethod
    def decode_token(self, token: str) -> UUID:
        pass
