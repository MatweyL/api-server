from abc import abstractmethod
from io import BytesIO
from typing import List

from server.adapters.outbound.s3_uploader.minio_uploader import MinioUploader
from server.domain.schemas import TaskGeneration, TaskAvatarGeneration, TaskChannelBannerGeneration, \
    TaskVideoPreviewGeneration, TaskImage, TaskStatus, TaskType
from server.domain.tasks.task_producer import TaskGenerationProducer
from server.domain.utils import generate_uid


class WorkerInterface:

    @abstractmethod
    async def generate(self, task: TaskGeneration) -> TaskGeneration:
        pass


class AbstractWorker(WorkerInterface):
    def __init__(self, uploader: MinioUploader,
                 task_video_preview_producer: TaskGenerationProducer,
                 task_avatar_producer: TaskGenerationProducer,
                 task_channel_banner_producer: TaskGenerationProducer,
                 bucket_name: str):
        self._uploader = uploader
        self._task_type_producer = {
            TaskType.VIDEO_PREVIEW_GENERATION: task_video_preview_producer,
            TaskType.AVATAR_GENERATION: task_avatar_producer,
            TaskType.CHANNEL_BANNER_GENERATION: task_channel_banner_producer
        }
        self._task_type_generation_methods = {
            TaskType.VIDEO_PREVIEW_GENERATION: self.generate_video_preview,
            TaskType.AVATAR_GENERATION: self.generate_avatar,
            TaskType.CHANNEL_BANNER_GENERATION: self.generate_channel_banner
        }
        self._bucket_name = bucket_name

    async def generate(self, task: TaskGeneration):
        task.task_status = TaskStatus.GENERATION_RUNNING
        task_producer = self._task_type_producer[task.task_type]
        await task_producer.produce(task)
        images_bytes: List[BytesIO] = await self._task_type_generation_methods[task.task_type](task)
        images = []
        for image_bytes in images_bytes:
            image_uid = f'{generate_uid()}.jpg'
            uploading_response = await self._uploader.upload(self._bucket_name, image_uid, image_bytes)
            image = TaskImage(image_uid=image_uid,
                              image_url=uploading_response.image_url,
                              task_uid=task.task_uid)
            images.append(image)
        task.task_status = TaskStatus.GENERATION_FINISHED
        task.task_images = images
        await task_producer.produce(task)

    @abstractmethod
    async def generate_video_preview(self, task: TaskVideoPreviewGeneration) -> List[BytesIO]:
        pass

    @abstractmethod
    async def generate_avatar(self, task: TaskAvatarGeneration) -> List[BytesIO]:
        pass

    @abstractmethod
    async def generate_channel_banner(self, task: TaskChannelBannerGeneration) -> List[BytesIO]:
        pass
