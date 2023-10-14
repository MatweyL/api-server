from typing import Optional

from server.common.config import BaseServiceConfig


class APIServerConfig(BaseServiceConfig):
    host: str
    port: int
    sentry_dsn: Optional[str]

    class Config:
        env_prefix = 'api_server_'


api_server_config = APIServerConfig()
