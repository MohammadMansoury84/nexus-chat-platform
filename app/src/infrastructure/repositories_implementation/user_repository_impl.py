from uuid import UUID

from sqlalchemy import exists, select
from sqlalchemy.ext.asyncio import AsyncSession
from src.domain.entities.User import User
from src.domain.repositories_Interface.user_repository import UserRepository
from src.infrastructure.Brief.user.get_by_id_brief import GetByIdBrief
from src.infrastructure.Brief.user.get_by_username_brief import GetByUserNameBrief
from src.infrastructure.Brief.user.list_all_brief import ListAllBrief
from src.infrastructure.database.orm_models.user_model import UserModel


class UserRepositoryImpl(UserRepository):
    def __init__(self, db: AsyncSession) -> None:
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

    async def get_by_id(self, user_id: UUID) -> GetByIdBrief | None:
        stmt = select(UserModel.id, UserModel.email, UserModel.username).where(
            UserModel.id == user_id
        )

        result = await self._db.execute(statement=stmt)
        row = result.first()

        if row is None:
            return None

        return GetByIdBrief(id=row.id, email=row.email, username=row.username)

    async def get_by_username(self, username: str) -> GetByUserNameBrief | None:
        stmt = select(UserModel.id, UserModel.hashed_password).where(
            UserModel.username == username
        )
        result = await self._db.execute(statement=stmt)
        row = result.first()

        if row is None:
            return None

        return GetByUserNameBrief(id=row.id, hashed_password=row.hashed_password)

    async def list_all(self) -> list[ListAllBrief]:
        stmt = select(UserModel)
        result = await self._db.scalars(statement=stmt)
        users = result.all()
        return [
            ListAllBrief(
                id=u.id, username=u.username, email=u.email, created_at=u.created_at
            )
            for u in users
        ]

    async def is_username_used(self, username: str) -> bool:
        stmt = select(exists().where(UserModel.username == username))
        return await self._db.scalar(stmt)

    async def is_email_used(self, email: str) -> bool:
        stmt = select(exists().where(UserModel.email == email))
        return await self._db.scalar(stmt)

    async def get_by_ids(self, user_ids: list[UUID]) -> list[GetByIdBrief]:
        if not user_ids:
            return []

        stmt = select(UserModel.id, UserModel.email, UserModel.username).where(
            UserModel.id.in_(user_ids)
        )

        result = await self._db.execute(statement=stmt)
        rows = result.all()

        return [
            GetByIdBrief(id=row.id, email=row.email, username=row.username) for row in rows
        ]
