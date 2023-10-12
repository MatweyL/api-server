from pydantic.v1 import BaseSettings

from .utils import get_env_path


class BaseServiceConfig(BaseSettings):
    log_level: str = "DEBUG"

    class Config:
        env_file = get_env_path()
        env_file_encoding = 'utf-8'


base_service_config = BaseServiceConfig()
