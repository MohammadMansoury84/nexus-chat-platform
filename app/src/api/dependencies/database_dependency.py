from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession
from src.infrastructure.database.session_db import get_async_session_local


async def get_session() -> AsyncGenerator[AsyncSession]:

    async with get_async_session_local() as session:
        try:
            yield session
            await session.commit()

        except Exception:
            await session.rollback()
            raise
