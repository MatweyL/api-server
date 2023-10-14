from io import BytesIO
from typing import Any, Dict, List

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from server.adapters.outbound.s3_uploader.minio_uploader import MinioUploader
from server.common.logs import logger
from server.domain.cruds import TaskGenerationCRUD, TaskVideoPreviewGenerationCRUD, TaskImageCRUD, \
    TaskAvatarGenerationCRUD, TaskChannelBannerGenerationCRUD
from server.domain.schemas import TaskStatus, TaskType, TaskGeneration, \
    InputTaskVideoPreviewGeneration, TaskVideoPreviewGeneration, TaskImage, InputTaskAvatarGeneration, \
    TaskAvatarGeneration, InputTaskChannelBannerGeneration, TaskChannelBannerGeneration
from server.domain.tasks.task_producer import AbstractTaskGenerationProducer
from server.domain.utils import generate_uid


class BaseGenerationService:

    def __init__(self):
        self._async_session: async_sessionmaker = None

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

    def __init__(self, task_producer: AbstractTaskGenerationProducer,
                 minio_uploader: MinioUploader, bucket_name: str):
        super().__init__()
        self._task_producer = task_producer
        self._minio_uploader = minio_uploader
        self._bucket_name = bucket_name

    async def create(self, video_author_comments: str,
                     tags: str, video: BytesIO, video_name) -> TaskVideoPreviewGeneration:
        uploading_response = await self._minio_uploader.upload(self._bucket_name,
                                                               f'{generate_uid()}_{video_name}', video)
        video_url = uploading_response.image_url
        input_task = InputTaskVideoPreviewGeneration(video_author_comments=video_author_comments,
                                                     tags=tags,
                                                     video_url=video_url)
        try:
            task_schema = TaskVideoPreviewGeneration(task_uid=generate_uid(),
                                                     task_status=TaskStatus.GENERATION_WAITING,
                                                     **input_task.model_dump())
            async with self._async_session.begin() as session:
                await TaskGenerationCRUD.create(task_schema, session)

            async with self._async_session.begin() as session:
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

    async def create(self, input_task: InputTaskAvatarGeneration, photo: BytesIO) -> TaskAvatarGeneration:
        try:
            task_schema = TaskAvatarGeneration(task_uid=generate_uid(),
                                               task_status=TaskStatus.GENERATION_WAITING,
                                               **input_task.model_dump())
            async with self._async_session.begin() as session:
                await TaskGenerationCRUD.create(task_schema, session)
            async with self._async_session.begin() as session:
                await TaskAvatarGenerationCRUD.create(task_schema, session)
            await self._task_producer.produce(task_schema)
            return task_schema
        except BaseException as e:
            logger.exception(e)

    async def get(self, task_uid: str) -> TaskAvatarGeneration:
        async with self._async_session.begin() as session:
            return await TaskAvatarGenerationCRUD.get(task_uid, session)


class TaskChannelBannerGenerationService(BaseGenerationService):

    def __init__(self, task_producer: AbstractTaskGenerationProducer):
        super().__init__()
        self._task_producer = task_producer

    async def create(self, input_task: InputTaskChannelBannerGeneration) -> TaskChannelBannerGeneration:
        try:
            task_schema = TaskChannelBannerGeneration(task_uid=generate_uid(),
                                                      task_status=TaskStatus.GENERATION_WAITING,
                                                      **input_task.model_dump())
            async with self._async_session.begin() as session:
                await TaskGenerationCRUD.create(task_schema, session)

            async with self._async_session.begin() as session:
                await TaskChannelBannerGenerationCRUD.create(task_schema, session)
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
                 task_avatar_gs: TaskAvatarGenerationService,
                 task_channel_banner_gs: TaskChannelBannerGenerationService,
                 task_image_s: TaskImageService):
        self._task_gs = task_gs
        self._task_image_s = task_image_s
        self._task_type_gs_map: Dict[TaskType, Any] = {
            TaskType.VIDEO_PREVIEW_GENERATION: task_video_preview_gs,
            TaskType.AVATAR_GENERATION: task_avatar_gs,
            TaskType.CHANNEL_BANNER_GENERATION: task_channel_banner_gs,
        }

    async def get(self, task_uid: str) -> TaskGeneration:
        task_base = await self._task_gs.get(task_uid)
        service = self._task_type_gs_map[task_base.task_type]
        task = await service.get(task_uid)

        if task.task_status == TaskStatus.GENERATION_FINISHED:
            task_images = await self._task_image_s.get_all(task_uid)
            task.task_images = task_images
        return task
