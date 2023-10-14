from server.adapters.outbound.producer.conifg import RabbitProducerConfig as ServerRabbitProducerConfig


class RabbitProducerConfig(ServerRabbitProducerConfig):

    class Config:
        env_prefix = 'rabbit_producer_ml_worker_'


rabbit_producer_config = RabbitProducerConfig()
