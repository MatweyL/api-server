import enum


class TaskType(str, enum.Enum):
    VIDEO_PREVIEW_GENERATION = "video_preview_generation"
    AVATAR_GENERATION = "avatar_photo_generation"
    CHANNEL_BANNER_GENERATION = "channel_banner_generation"


class TaskStatus(str, enum.Enum):
    TEXT_EXTRACTION_WAITING = "text_extraction_waiting"
    TEXT_EXTRACTION_RUNNING = "text_extraction_running"
    TEXT_EXTRACTION_FAILED = "text_extraction_failed"
    TEXT_EXTRACTION_FINISHED = "text_extraction_finished"
    GENERATION_WAITING = "generation_waiting"
    GENERATION_RUNNING = "generation_running"
    GENERATION_FAILED = "generation_failed"
    GENERATION_FINISHED = "generation_finished"
