from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from service.common.logs import logger
from service.domain.cruds import TaskGenerationCRUD, TaskVideoPreviewGenerationCRUD
from service.domain.schemas import InputTaskGeneration, TaskStatus, TaskType, TaskGeneration, \
    InputTaskVideoPreviewGeneration, TaskVideoPreviewGeneration
from service.domain.task_producer import TaskProducer
from service.domain.utils import generate_uid


class TaskGenerationService:

    def __init__(self, async_session: async_sessionmaker[AsyncSession]):
        self._async_session = async_session

    async def update_status(self, task_uid: str, new_task_status: TaskStatus):
        async with self._async_session.begin() as session:
            await TaskGenerationCRUD.update_status(task_uid, new_task_status, session)


class TaskVideoPreviewGenerationService:

    def __init__(self, task_producer: TaskProducer):
        self._task_producer = task_producer
        self._async_session = None

    def set_async_session(self, async_session: async_sessionmaker[AsyncSession]):
        self._async_session = async_session

    async def create(self, input_task: InputTaskVideoPreviewGeneration) -> TaskVideoPreviewGeneration:
        try:
            task_schema = TaskVideoPreviewGeneration(task_uid=generate_uid(),
                                                     task_status=TaskStatus.TEXT_EXTRACTION_WAITING,
                                                     **input_task.model_dump())
            async with self._async_session.begin() as session:
                await TaskGenerationCRUD.create(task_schema, session)
                await TaskVideoPreviewGenerationCRUD.create(task_schema, session)
            await self._task_producer.produce(task_schema)
            return task_schema
        except BaseException as e:
            logger.exception(e)
