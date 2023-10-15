from io import BytesIO
from typing import List

from ml_worker.core.worker import AbstractWorker
from server.domain.schemas import TaskVideoPreviewGeneration, TaskAvatarGeneration, \
    TaskChannelBannerGeneration


class Worker(AbstractWorker):

    async def generate_video_preview(self, task: TaskVideoPreviewGeneration) -> List[BytesIO]:
        return [get_bytes_io()]

    async def generate_avatar(self, task: TaskAvatarGeneration) -> List[BytesIO]:
        return [get_bytes_io()]

    async def generate_channel_banner(self, task: TaskChannelBannerGeneration) -> List[BytesIO]:
        return [get_bytes_io()]


def get_bytes_io():
    return BytesIO(b'mock')
