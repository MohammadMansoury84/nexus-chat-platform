from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Setting(BaseSettings):
    show_log_in_cli: bool
    jwt_secret_key: SecretStr
    jwt_algorithm: str
    access_token_expire_minutes: int
    darabase_url: str
    pool_timeout: int
    pool_size: int
    echo: bool
    isolated: str

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")
