from server.common.config import BaseServiceConfig


class TaskProducerConfig(BaseServiceConfig):
    video_preview_queue_name: str
    avatar_queue_name: str
    channel_banner_queue_name: str

    class Config:
        env_prefix = 'task_producer_'


task_producer_config = TaskProducerConfig()


class TaskUpdatesConsumerConfig(BaseServiceConfig):
    video_preview_queue_name: str
    avatar_queue_name: str
    channel_banner_queue_name: str

    class Config:
        env_prefix = 'task_updates_consumer_'


task_updates_consumer_config = TaskUpdatesConsumerConfig()
