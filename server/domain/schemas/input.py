from typing import Optional

from pydantic import BaseModel

from server.domain.schemas import TaskType


class InputTaskGeneration(BaseModel):
    task_type: TaskType


class InputTaskVideoPreviewGeneration(InputTaskGeneration):
    task_type: TaskType = TaskType.VIDEO_PREVIEW_GENERATION
    video_url: str
    video_author_comments: Optional[str]
    tags: Optional[str]


class InputTaskAvatarGeneration(InputTaskGeneration):
    task_type: TaskType = TaskType.AVATAR_GENERATION
    avatar_description: str


class InputTaskChannelBannerGeneration(InputTaskGeneration):
    task_type: TaskType = TaskType.CHANNEL_BANNER_GENERATION
    channel_banner_description: str
