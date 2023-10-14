from abc import abstractmethod

from server.domain.schemas import TaskGeneration, TaskStatus
from server.domain.services.main import TaskGenerationService, TaskImageService
from server.ports.inbound import RabbitConsumerInterface


class AbstractTaskGenerationConsumer:

    def __init__(self,
                 rabbit_consumer: RabbitConsumerInterface,
                 queue_name: str):
        self._rabbit_consumer = rabbit_consumer
        self._queue_name = queue_name

    @abstractmethod
    async def consume(self, task: TaskGeneration):
        pass

    @abstractmethod
    async def _rabbit_consume_callback(self, task_raw: str):
        pass

    async def setup(self):
        await self._rabbit_consumer.consume_queue(self._queue_name,
                                                  self._rabbit_consume_callback)


class TaskGenerationUpdatesConsumerMock(AbstractTaskGenerationConsumer):

    async def consume(self, task: TaskGeneration):
        pass

    async def _rabbit_consume_callback(self, task_raw: str):
        pass

    async def setup(self):
        pass


class TaskGenerationUpdatesConsumer(AbstractTaskGenerationConsumer):

    def __init__(self, rabbit_consumer: RabbitConsumerInterface, queue_name: str, task_gs: TaskGenerationService,
                 task_image_s: TaskImageService):
        super().__init__(rabbit_consumer, queue_name)
        self._task_gs = task_gs
        self._task_image_s = task_image_s

    async def _rabbit_consume_callback(self, task_raw: str):
        task = TaskGeneration.model_validate_json(task_raw)
        await self.consume(task)

    async def consume(self, task: TaskGeneration):
        await self._task_gs.update_status(task.task_uid, task.task_status)
        if task.task_status == TaskStatus.GENERATION_FINISHED:
            await self._task_image_s.create_all(task.task_images)
