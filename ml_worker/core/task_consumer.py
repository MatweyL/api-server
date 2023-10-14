from ml_worker.core.utils import task_type_schema_map
from ml_worker.core.worker import WorkerInterface
from server.common.logs import logger
from server.domain.schemas import TaskGeneration
from server.domain.tasks.task_updates_consumer import AbstractTaskGenerationConsumer
from server.ports.inbound import RabbitConsumerInterface


class TaskGenerationConsumer(AbstractTaskGenerationConsumer):

    def __init__(self, rabbit_consumer: RabbitConsumerInterface, queue_name: str, worker: WorkerInterface):
        super().__init__(rabbit_consumer, queue_name)
        self._worker = worker

    async def consume(self, task: TaskGeneration):
        await self._worker.generate(task)

    async def _rabbit_consume_callback(self, task_raw: str):
        task_input = TaskGeneration.model_validate_json(task_raw)
        task_schema = task_type_schema_map[task_input.task_type]
        task = task_schema.model_validate_json(task_raw)
        logger.debug('converted task_raw to schema')
        await self.consume(task)
