from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr


class Setting(BaseSettings):
    show_log_in_cli: bool
    jwt_secret_key: SecretStr
    jwt_algorithm: str
    access_token_expire_minutes: int

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")
