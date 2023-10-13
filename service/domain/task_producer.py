from abc import abstractmethod

from service.common.logs import logger
from service.domain.schemas import TaskGeneration


class TaskProducer:

    def __init__(self):
        pass

    @abstractmethod
    async def produce(self, task: TaskGeneration):
        pass


class TaskProducerMock(TaskProducer):

    async def produce(self, task: TaskGeneration):
        logger.info(f'produced {task}')