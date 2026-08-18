from sqlalchemy.ext.asyncio import create_async_engine
from src.core.config.Setting import Setting

setting = Setting()

async_engine = create_async_engine(
    url=setting.database_url,
    echo=setting.echo,
    pool_timeout=setting.pool_timeout,
    pool_size=setting.pool_size,
    isolated_level=setting.isolated_level,
)
