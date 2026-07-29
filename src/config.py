from pydantic_settings import BaseSettings, SettingsConfigDict


class Setting(BaseSettings):
    show_log_in_cli: bool

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")
