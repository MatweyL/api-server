import asyncio
from typing import Callable, Optional

from aio_pika import connect_robust
from aio_pika.abc import AbstractChannel, AbstractConnection, AbstractIncomingMessage

from server.adapters.inbound.consumer.utils import _build_connection_url
from server.ports.inbound import RabbitConsumerInterface

try:
    from server.common.logs import logger
except ImportError:
    import logging
    logger = logging
    logger.warning('failed to import project logger; use default logging')


class RabbitConsumer(RabbitConsumerInterface):

    def __init__(self, protocol: str, user: str, password: str, host: str, port: str, virtual_host: str):
        self._connection_url = _build_connection_url(protocol, user, password, host, port, virtual_host)
        self._reconnect_timeout_s = 5
        self._connection: Optional[AbstractConnection] = None
        self._channel: Optional[AbstractChannel] = None

    async def _create_connection(self):
        try:
            connection = await connect_robust(self._connection_url)
        except BaseException as e:
            logger.warning(f'{self} cannot create connection: {e}; '
                           f'sleep {self._reconnect_timeout_s} s and retry')
            await asyncio.sleep(self._reconnect_timeout_s)
            return await self._create_connection()
        else:
            return connection

    async def start(self):
        self._connection = await self._create_connection()
        self._channel = await  self._connection.channel()
        logger.info(f'{self} started')

    async def stop(self):
        if not self._connection.is_closed:
            await self._connection.close()
        logger.info(f'{self} stopped')

    def _processing_callback_bridge(self, processing_callback: Callable):
        async def inner(message: AbstractIncomingMessage):
            async with message.process():
                message_str = message.body.decode('utf-8')
            logger.debug(f'{self} got message')
            await processing_callback(message_str)

        return inner

    async def consume_queue(self, queue_name: str, processing_callback: Callable):
        queue = await self._channel.declare_queue(queue_name)
        await queue.consume(self._processing_callback_bridge(processing_callback))
        logger.info(f'{self} start consuming {queue_name}')
