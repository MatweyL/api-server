from abc import abstractmethod
from typing import Callable


class RabbitConsumerInterface:

    @abstractmethod
    async def start(self):
        pass

    @abstractmethod
    async def stop(self):
        pass

    @abstractmethod
    async def consume_queue(self, queue_name: str, processing_callback: Callable):
        pass
