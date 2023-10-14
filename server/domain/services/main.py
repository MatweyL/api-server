from typing import Any, Dict, List

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from server.common.logs import logger
from server.domain.cruds import TaskGenerationCRUD, TaskVideoPreviewGenerationCRUD, TaskImageCRUD, \
    TaskAvatarGenerationCRUD
from server.domain.schemas import TaskStatus, TaskType, TaskGeneration, \
    InputTaskVideoPreviewGeneration, TaskVideoPreviewGeneration, TaskImage, InputTaskAvatarGeneration, \
    TaskAvatarGeneration
from server.domain.tasks.task_producer import AbstractTaskGenerationProducer
from server.domain.utils import generate_uid


class BaseGenerationService:

    def __init__(self):
        self._async_session = None

    def set_async_session(self, async_session: async_sessionmaker[AsyncSession]):
        self._async_session = async_session


class TaskGenerationService(BaseGenerationService):

    async def update_status(self, task_uid: str, new_task_status: TaskStatus):
        async with self._async_session.begin() as session:
            await TaskGenerationCRUD.update_status(task_uid, new_task_status, session)

    async def get(self, task_uid: str) -> TaskGeneration:
        async with self._async_session.begin() as session:
            return await TaskGenerationCRUD.get(task_uid, session)


class TaskVideoPreviewGenerationService(BaseGenerationService):

    def __init__(self, task_producer: AbstractTaskGenerationProducer):
        super().__init__()
        self._task_producer = task_producer

    async def create(self, input_task: InputTaskVideoPreviewGeneration) -> TaskVideoPreviewGeneration:
        try:
            task_schema = TaskVideoPreviewGeneration(task_uid=generate_uid(),
                                                     task_status=TaskStatus.GENERATION_WAITING,
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


class TaskAvatarGenerationService(BaseGenerationService):

    def __init__(self, task_producer: AbstractTaskGenerationProducer):
        super().__init__()
        self._task_producer = task_producer

    async def create(self, input_task: InputTaskAvatarGeneration) -> TaskAvatarGeneration:
        try:
            task_schema = TaskAvatarGeneration(task_uid=generate_uid(),
                                               task_status=TaskStatus.GENERATION_WAITING,
                                               **input_task.model_dump())
            async with self._async_session.begin() as session:
                await TaskGenerationCRUD.create(task_schema, session)
                await TaskAvatarGenerationCRUD.create(task_schema, session)
            await self._task_producer.produce(task_schema)
            return task_schema
        except BaseException as e:
            logger.exception(e)

    async def get(self, task_uid: str) -> TaskAvatarGeneration:
        async with self._async_session.begin() as session:
            return await TaskAvatarGenerationCRUD.get(task_uid, session)


class TaskVideoPreviewGenerationService(BaseGenerationService):

    def __init__(self, task_producer: AbstractTaskGenerationProducer):
        super().__init__()
        self._task_producer = task_producer

    async def create(self, input_task: InputTaskVideoPreviewGeneration) -> TaskVideoPreviewGeneration:
        try:
            task_schema = TaskVideoPreviewGeneration(task_uid=generate_uid(),
                                                     task_status=TaskStatus.GENERATION_WAITING,
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


class TaskImageService(BaseGenerationService):

    async def get_all(self, task_uid: str) -> List[TaskImage]:
        async with self._async_session.begin() as session:
            return await TaskImageCRUD.get_all(task_uid, session)

    async def create_all(self, tasks_images: List[TaskImage]):
        async with self._async_session.begin() as session:
            await TaskImageCRUD.create_all(tasks_images, session)


class TaskGenerationFacade:

    def __init__(self, task_gs: TaskGenerationService,
                 task_video_preview_gs: TaskVideoPreviewGenerationService,
                 task_image_s: TaskImageService):
        self._task_gs = task_gs
        self._task_video_preview_gs = task_video_preview_gs
        self._task_image_s = task_image_s
        self._task_type_gs_map: Dict[TaskType, Any] = {
            TaskType.VIDEO_PREVIEW_GENERATION: self._task_video_preview_gs
        }

    async def get(self, task_uid: str) -> TaskGeneration:
        task_base = await self._task_gs.get(task_uid)
        service = self._task_type_gs_map[task_base.task_type]
        task = await service.get(task_uid)

        if task.task_status == TaskStatus.GENERATION_FINISHED:
            task_images = await self._task_image_s.get_all(task_uid)
            task.task_images = task_images
        return task
