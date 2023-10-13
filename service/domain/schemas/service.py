from typing import Optional, List

from pydantic import BaseModel, Field

from service.domain.schemas.base import TaskType, TaskStatus


class TaskImage(BaseModel):
    image_uid: str
    image_url: str
    task_uid: str


class TaskGeneration(BaseModel):
    task_uid: str
    task_type: TaskType
    task_status: TaskStatus
    task_images: List[TaskImage] = Field(default_factory=list)


class TaskVideoPreviewGeneration(TaskGeneration):
    task_type: TaskType = TaskType.VIDEO_PREVIEW_GENERATION
    video_url: str
    video_text: Optional[str] = None
    video_author_comments: Optional[str] = None
    tags: Optional[str] = None


class TaskAvatarGeneration(TaskGeneration):
    task_type: TaskType = TaskType.AVATAR_GENERATION
    avatar_description: str


class TaskChannelBannerGeneration(TaskGeneration):
    task_type: TaskType = TaskType.CHANNEL_BANNER_GENERATION
    channel_banner_description: str


