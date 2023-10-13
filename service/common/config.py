from pydantic.v1 import BaseSettings

from .utils import get_env_path


class BaseServiceConfig(BaseSettings):

    class Config:
        env_file = get_env_path()
        env_file_encoding = 'utf-8'


class LogConfig(BaseServiceConfig):
    log_level: str = "DEBUG"


class DatabaseConfig(BaseServiceConfig):
    driver: str = 'postgresql'
    host: str
    port: int
    user: str
    password: str
    name: str

    class Config:
        env_prefix = 'db_'


db_config = DatabaseConfig()
log_config = LogConfig()

