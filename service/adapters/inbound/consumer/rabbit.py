from typing import Callable

from service.ports.inbound import RabbitConsumerInterface


class RabbitConsumer(RabbitConsumerInterface):
    async def start(self):
        pass

    async def stop(self):
        pass

    async def consume_queue(self, queue_name: str, processing_callback: Callable):
        pass
