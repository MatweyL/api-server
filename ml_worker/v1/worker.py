from io import BytesIO
from typing import List

from ml_worker.core.worker import AbstractWorker
from ml_worker.v1.RutubeCase import generate_video_preview
from server.domain.schemas import TaskVideoPreviewGeneration, TaskAvatarGeneration, \
    TaskChannelBannerGeneration


class MockWorker(AbstractWorker):

    def generate_video_preview(self, task: TaskVideoPreviewGeneration) -> List[BytesIO]:
        return [get_bytes_io()]

    def generate_avatar(self, task: TaskAvatarGeneration) -> List[BytesIO]:
        return [get_bytes_io()]

    def generate_channel_banner(self, task: TaskChannelBannerGeneration) -> List[BytesIO]:
        return [get_bytes_io()]


class Worker(AbstractWorker):

    def generate_video_preview(self, task: TaskVideoPreviewGeneration) -> List[BytesIO]:
        return [BytesIO(img_bytes) for img_bytes in generate_video_preview(None, task.video_author_comments, task.tags)]

    def generate_avatar(self, task: TaskAvatarGeneration) -> List[BytesIO]:
        pass

    def generate_channel_banner(self, task: TaskChannelBannerGeneration) -> List[BytesIO]:
        pass
