from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Setting(BaseSettings):
    show_log_in_cli: bool
    jwt_secret_key: SecretStr
    jwt_algorithm: str
    access_token_expire_minutes: int
    database_url: str
    pool_timeout: int
    pool_size: int
    echo: bool
    isolation_level: str
    max_overflow: int

    model_config = SettingsConfigDict(env_file="app/.env", env_file_encoding="utf-8")
