from typing import Any, Dict

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from service.common.logs import logger
from service.domain.cruds import TaskGenerationCRUD, TaskVideoPreviewGenerationCRUD
from service.domain.schemas import TaskStatus, TaskType, TaskGeneration, \
    InputTaskVideoPreviewGeneration, TaskVideoPreviewGeneration
from service.domain.task_producer import TaskProducer
from service.domain.utils import generate_uid


class TaskGenerationService:

    def __init__(self):
        self._async_session = None

    def set_async_session(self, async_session: async_sessionmaker[AsyncSession]):
        self._async_session = async_session

    async def update_status(self, task_uid: str, new_task_status: TaskStatus):
        async with self._async_session.begin() as session:
            await TaskGenerationCRUD.update_status(task_uid, new_task_status, session)

    async def get(self, task_uid: str) -> TaskGeneration:
        async with self._async_session.begin() as session:
            return await TaskGenerationCRUD.get(task_uid, session)


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

    async def get(self, task_uid: str) -> TaskVideoPreviewGeneration:
        async with self._async_session.begin() as session:
            return await TaskVideoPreviewGenerationCRUD.get(task_uid, session)

class TaskGenerationFacade:

    def __init__(self, task_gs: TaskGenerationService,
                 task_video_preview_gs: TaskVideoPreviewGenerationService):
        self._task_gs = task_gs
        self._task_video_preview_gs = task_video_preview_gs
        self._task_type_gs_map: Dict[TaskType, Any] = {
            TaskType.VIDEO_PREVIEW_GENERATION: self._task_video_preview_gs
        }

    async def get(self, task_uid: str):
        task_generation = await self._task_gs.get(task_uid)
        if task_generation.task_status == TaskStatus.GENERATION_FINISHED:
            task_images = []
            task_generation.task_images = task_images
        service = self._task_type_gs_map[task_generation.task_type]

