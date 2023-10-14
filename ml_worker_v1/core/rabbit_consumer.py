from server.adapters.inbound.consumer.conifg import RabbitConsumerConfig as ServerRabbitConsumerConfig


class RabbitConsumerConfig(ServerRabbitConsumerConfig):

    class Config:
        env_prefix = 'rabbit_consumer_ml_worker_'


rabbit_consumer_config = RabbitConsumerConfig()
