from abc import abstractmethod, ABC

from service.common.logs import logger
from service.domain.schemas import TaskGeneration
from service.ports.outbound import RabbitProducerInterface


class AbstractTaskGenerationProducer(ABC):

    def __init__(self, rabbit_producer: RabbitProducerInterface, queue_name: str):
        self._rabbit_producer = rabbit_producer
        self._queue_name = queue_name

    @abstractmethod
    async def produce(self, task: TaskGeneration):
        pass


class TaskGenerationProducerMock(AbstractTaskGenerationProducer):

    async def produce(self, task: TaskGeneration):
        logger.info(f'produced {task}')


class TaskGenerationProducer(AbstractTaskGenerationProducer):

    async def produce(self, task: TaskGeneration):
        task_bytes = task.model_dump_json().encode('utf-8')
        await self._rabbit_producer.produce(task_bytes, task.task_uid, self._queue_name)
