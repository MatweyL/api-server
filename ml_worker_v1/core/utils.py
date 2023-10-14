from server.domain.schemas import TaskType, TaskAvatarGeneration, TaskVideoPreviewGeneration, \
    TaskChannelBannerGeneration

task_type_schema_map = {
            TaskType.VIDEO_PREVIEW_GENERATION: TaskVideoPreviewGeneration,
            TaskType.AVATAR_GENERATION: TaskAvatarGeneration,
            TaskType.CHANNEL_BANNER_GENERATION: TaskChannelBannerGeneration
        }
