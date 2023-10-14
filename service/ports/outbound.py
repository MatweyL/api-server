from abc import abstractmethod


class RabbitProducerInterface:

    @abstractmethod
    async def start(self):
        pass

    @abstractmethod
    async def stop(self):
        pass

    @abstractmethod
    async def produce(self, body: bytes, correlation_id: str, routing_key: str):
        pass

    def __repr__(self):
        return self.__class__.__name__
