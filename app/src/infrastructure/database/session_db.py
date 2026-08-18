from sqlalchemy.ext.asyncio import async_sessionmaker
from src.infrastructure.database.detabase_set_up import get_async_engine

AsyncSessionLocal = async_sessionmaker(
    bind=get_async_engine,
    expire_on_commit=False,
    autoflush=False,
)
