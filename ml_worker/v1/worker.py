from io import BytesIO
from typing import List

from ml_worker.core.worker import AbstractWorker
from ml_worker.v1.RutubeCase import generate_video_preview
from server.domain.schemas import TaskVideoPreviewGeneration, TaskAvatarGeneration, \
    TaskChannelBannerGeneration


class Worker(AbstractWorker):

    async def generate_video_preview(self, task: TaskVideoPreviewGeneration) -> List[BytesIO]:
        return [BytesIO(img_bytes) for img_bytes in generate_video_preview(None, task.video_author_comments, task.tags)]

    async def generate_avatar(self, task: TaskAvatarGeneration) -> List[BytesIO]:
        pass

    async def generate_channel_banner(self, task: TaskChannelBannerGeneration) -> List[BytesIO]:
        pass
