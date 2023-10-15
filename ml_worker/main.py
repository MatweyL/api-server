import asyncio

from ml_worker.core.minio_uploader import minio_uploader_config
from ml_worker.core.rabbit_consumer import rabbit_consumer_config
from ml_worker.core.rabbit_producer import rabbit_producer_config
from ml_worker.core.task_consumer import TaskGenerationConsumer
from ml_worker.v1.worker import Worker
from server.adapters.inbound.consumer.rabbit import RabbitConsumer
from server.adapters.outbound.producer.rabbit import RabbitProducer
from server.adapters.outbound.s3_uploader.minio_uploader import MinioUploader
from server.common.logs import logger
from server.domain.config import task_producer_config as task_consumer_config
from server.domain.config import task_updates_consumer_config as task_producer_config
from server.domain.tasks.task_producer import TaskGenerationProducer


async def main():
    rabbit_producer = RabbitProducer(rabbit_producer_config.protocol,
                                     rabbit_producer_config.user,
                                     rabbit_producer_config.password,
                                     rabbit_producer_config.host,
                                     rabbit_producer_config.port,
                                     rabbit_producer_config.virtual_host,
                                     rabbit_producer_config.exchange_name,
                                     rabbit_producer_config.exchange_type, )
    rabbit_consumer = RabbitConsumer(rabbit_consumer_config.protocol,
                                     rabbit_consumer_config.user,
                                     rabbit_consumer_config.password,
                                     rabbit_consumer_config.host,
                                     rabbit_consumer_config.port,
                                     rabbit_consumer_config.virtual_host, )
    minio_uploader = MinioUploader(minio_uploader_config.host, minio_uploader_config.user,
                                   minio_uploader_config.password, minio_uploader_config.max_retries,
                                   minio_uploader_config.before_retry_timeout_s)

    task_video_preview_producer = TaskGenerationProducer(rabbit_producer, task_producer_config.video_preview_queue_name)
    task_avatar_producer = TaskGenerationProducer(rabbit_producer, task_producer_config.avatar_queue_name)
    task_channel_banner_producer = TaskGenerationProducer(rabbit_producer,
                                                          task_producer_config.channel_banner_queue_name)
    worker_video_preview = Worker(minio_uploader, task_video_preview_producer, task_avatar_producer,
                                  task_channel_banner_producer, minio_uploader_config.bucket_name)

    task_video_preview_consumer = TaskGenerationConsumer(rabbit_consumer,
                                                         task_consumer_config.video_preview_queue_name,
                                                         worker_video_preview)

    await rabbit_producer.start()
    await rabbit_consumer.start()

    task_consumers = [task_video_preview_consumer]
    for task_consumer in task_consumers:
        await task_consumer.setup()

    try:
        await asyncio.Future()
    except BaseException as e:
        logger.exception(e)
    await rabbit_producer.stop()
    await rabbit_consumer.stop()


if __name__ == "__main__":
    asyncio.run(main())
