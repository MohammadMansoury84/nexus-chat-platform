from uuid import UUID

from sqlalchemy import exists, select
from sqlalchemy.ext.asyncio import AsyncSession
from src.domain.entities.User import User
from src.domain.repositories_Interface.user_repository import UserRepository
from src.infrastructure.database.orm_models.user_model import UserModel


class UserRepositoryImpl(UserRepository):
    def __init__(self, db: AsyncSession) -> None:
        self._users: list[User] = []
        self._logged_in_user_ids: set[UUID] = set()
        self._db = db

    def add(self, user: User) -> User:
        orm_user = UserModel(
            id=user.id,
            username=user.username,
            email=user.email,
            hashed_password=user.hashed_password,
            created_at=user.created_at,
        )
        self._db.add(orm_user)
        return user

    def get_by_id(self, user_id: UUID) -> User | None:
        for user in self._users:
            if user.id == user_id:
                return user

        return None

    async def get_by_username(self, username: str) -> dict | None:
        stmt = select(UserModel.id, UserModel.hashed_password).where(
            UserModel.username == username
        )
        result = await self._db.execute(statement=stmt)
        row = result.first()

        if row is None:
            return None

        return {"id": row.id, "hashed_password": row.hashed_password}

    def list_all(self) -> list[User]:
        return self._users

    async def is_username_used(self, username: str) -> bool:
        stmt = select(exists().where(UserModel.username == username))
        return await self._db.scalar(stmt)

    async def is_email_used(self, email: str) -> bool:
        stmt = select(exists().where(UserModel.email == email))
        return await self._db.scalar(stmt)

    def add_user_id_to_logged_in_user_ids(self, user_id: UUID) -> UUID:
        self._logged_in_user_ids.add(user_id)
        return user_id

    def remove_user_id_in_logged_in_user_ids(self, user_id: UUID) -> None:

        if user_id in self._logged_in_user_ids:
            self._logged_in_user_ids.remove(user_id)

    def get_logged_in_user_ids(self) -> set[UUID]:
        return self._logged_in_user_ids

    def is_user_logged_in(self, user_id: UUID) -> bool:
        return user_id in self._logged_in_user_ids
