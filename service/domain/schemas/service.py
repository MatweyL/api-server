from typing import Optional, List

from pydantic import BaseModel

from service.domain.schemas.base import TaskType, TaskStatus


class TaskGeneration(BaseModel):
    task_uid: str
    task_type: TaskType
    task_status: TaskStatus
    task_images_urls: List[str]


class TaskVideoPreviewGeneration(TaskGeneration):
    video_url: str
    video_text: Optional[str]
    video_author_comments: Optional[str]


class TaskAvatarGeneration(TaskGeneration):
    avatar_description: str


class TaskChannelBannerGeneration(TaskGeneration):
    channel_banner_description: str



