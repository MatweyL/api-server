from typing import Optional

from service.common.config import BaseServiceConfig


class RabbitConsumerConfig(BaseServiceConfig):
    protocol: str = "amqp"
    user: str
    password: str
    host: str
    port: Optional[int]
    virtual_host: str = "/"

    class Config:
        env_prefix = 'rabbit_consumer_'


rabbit_consumer_config = RabbitConsumerConfig()
