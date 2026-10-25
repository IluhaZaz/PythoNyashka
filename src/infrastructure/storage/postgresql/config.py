from pydantic_settings import BaseSettings


class DBConfig(BaseSettings):
    host: str = "localhost"
    user: str = "admin"
    password: str = "pass"
    port: str = '5442'
    db: str = 'pitonyashka'
