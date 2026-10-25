from pydantic_settings import BaseSettings, SettingsConfigDict


class DBConfig(BaseSettings):
    host: str = "localhost"
    user: str = "admin"
    password: str = "pass"
    port: str = '5442'
    name: str = 'pitonyashka'

    model_config = SettingsConfigDict(env_prefix="db_")
