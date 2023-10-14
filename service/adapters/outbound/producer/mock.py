from service.ports.outbound import RabbitProducerInterface


class RabbitProducerMock(RabbitProducerInterface):

    async def start(self):
        pass

    async def stop(self):
        pass

    async def produce(self, body: bytes, correlation_id: str, routing_key: str):
        pass
