import asyncio
from abc import abstractmethod
from typing import Optional

from aio_pika import Message, connect_robust
from aio_pika.abc import AbstractExchange, AbstractConnection

from service.ports.outbound import RabbitProducerInterface
from .utils import _build_connection_url

try:
    from service.common.logs import logger
except ImportError:
    import logging
    logger = logging
    logger.warning('failed to import project logger; use default logging')


class RabbitProducer(RabbitProducerInterface):

    def __init__(self, protocol: str, user: str, password: str, host: str, port: str, virtual_host: str,
                 exchange_name: str, exchange_type: str, ):
        self._connection_url = _build_connection_url(protocol, user, password, host, port, virtual_host)
        self._exchange_name = exchange_name
        self._exchange_type = exchange_type

        self._reconnect_timeout_s = 5
        self._produce_max_retries = 5
        self._connection: Optional[AbstractConnection] = None
        self._exchange: Optional[AbstractExchange] = None

    async def start(self):
        try:
            self._connection = await connect_robust(self._connection_url)
        except BaseException as e:
            logger.warning(f'cannot create connection: {e}; sleep {self._reconnect_timeout_s} s and retry')
            await asyncio.sleep(self._reconnect_timeout_s)
            return await self.start()
        else:
            channel = await self._connection.channel()
            self._exchange = await channel.declare_exchange(self._exchange_name, self._exchange_type)
            logger.info(f'started')

    async def stop(self):
        if not self._connection.is_closed:
            await self._connection.close()

    async def produce(self, body: bytes, correlation_id: str, routing_key: str):
        current_retry = 0
        while current_retry < self._produce_max_retries:
            try:
                await self._exchange.publish(Message(body=body,
                                                     correlation_id=correlation_id,),
                                             routing_key=routing_key)
            except BaseException as e:
                logger.error(f'retry: [{current_retry}|{self._produce_max_retries}]; '
                             f'got exception while data producing: {e}')
                logger.exception(e)
                current_retry += 1
            else:
                break

