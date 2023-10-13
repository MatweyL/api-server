from typing import Optional

from service.common.config import BaseServiceConfig


class RabbitProducerConfig(BaseServiceConfig):
    protocol: str = "amqp"
    user: str
    password: str
    host: str
    exchange_name: str
    exchange_type: str
    port: Optional[int]
    virtual_host: str = "/"

    class Config:
        env_prefix = 'rabbit_producer_'


rabbit_error_producer_config = RabbitProducerConfig()
