from io import BytesIO
from typing import Union, Annotated

from fastapi import APIRouter, HTTPException, UploadFile
from fastapi.params import File, Form
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from server.adapters.inbound.consumer.conifg import rabbit_consumer_config
from server.adapters.inbound.consumer.rabbit import RabbitConsumer
from server.adapters.outbound.producer.conifg import rabbit_producer_config
from server.adapters.outbound.producer.rabbit import RabbitProducer
from server.adapters.outbound.s3_uploader.config import minio_uploader_config
from server.adapters.outbound.s3_uploader.minio_uploader import MinioUploader
from server.common.config import db_config
from server.common.logs import logger
from server.common.utils import get_db_url
from server.domain.config import task_producer_config, task_updates_consumer_config
from server.domain.schemas import InputTaskVideoPreviewGeneration, InputTaskAvatarGeneration, \
    InputTaskChannelBannerGeneration
from server.domain.schemas.main import TaskVideoPreviewGeneration, TaskAvatarGeneration, \
    TaskChannelBannerGeneration
from server.domain.services.main import TaskVideoPreviewGenerationService, TaskGenerationService, TaskGenerationFacade, \
    TaskImageService, TaskAvatarGenerationService, TaskChannelBannerGenerationService
from server.domain.tasks.task_producer import TaskGenerationProducer
from server.domain.tasks.task_updates_consumer import TaskGenerationUpdatesConsumer

router_tasks = APIRouter(prefix='/tasks')

minio_uploader = MinioUploader(minio_uploader_config.host,
                               minio_uploader_config.user,
                               minio_uploader_config.password,
                               minio_uploader_config.max_retries,
                               minio_uploader_config.before_retry_timeout_s)

# REGION RABBITMQ PRODUCERS
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

# REGION SERVICE TASK PRODUCERS
task_video_preview_generation_producer = TaskGenerationProducer(rabbit_producer,
                                                                task_producer_config.video_preview_queue_name)
task_avatar_generation_producer = TaskGenerationProducer(rabbit_producer,
                                                         task_producer_config.avatar_queue_name)
task_channel_banner_generation_producer = TaskGenerationProducer(rabbit_producer,
                                                                 task_producer_config.channel_banner_queue_name)

# REGION SERVICES
task_gs = TaskGenerationService()
task_image_s = TaskImageService()
task_video_preview_gs = TaskVideoPreviewGenerationService(task_video_preview_generation_producer,
                                                          minio_uploader,
                                                          minio_uploader_config.bucket_name)
task_avatar_gs = TaskAvatarGenerationService(task_avatar_generation_producer)
task_channel_banner_gs = TaskChannelBannerGenerationService(task_channel_banner_generation_producer)

# REGION UPDATES CONSUMERS
task_video_preview_generation_updates_consumer = TaskGenerationUpdatesConsumer(rabbit_consumer,
                                                                               task_updates_consumer_config.video_preview_queue_name,
                                                                               task_gs, task_image_s)
task_avatar_generation_updates_consumer = TaskGenerationUpdatesConsumer(rabbit_consumer,
                                                                        task_updates_consumer_config.avatar_queue_name,
                                                                        task_gs, task_image_s)
task_channel_banner_generation_updates_consumer = TaskGenerationUpdatesConsumer(rabbit_consumer,
                                                                                task_updates_consumer_config.channel_banner_queue_name,
                                                                                task_gs, task_image_s)

task_facade = TaskGenerationFacade(task_gs, task_video_preview_gs, task_avatar_gs, task_channel_banner_gs, task_image_s)


async def upload_file_as_bytes_io(file: UploadFile) -> BytesIO:
    file_bytes_io = BytesIO()
    chunk_size = 1024
    while True:
        chunk = await file.read(chunk_size)
        if not chunk:
            break
        file_bytes_io.write(chunk)
    return file_bytes_io


@router_tasks.get('/', response_model=Union[TaskVideoPreviewGeneration,
                                            TaskAvatarGeneration,
                                            TaskChannelBannerGeneration],
                  status_code=200)
async def get_task_by_uid(task_uid: str):
    task = await task_facade.get(task_uid)
    if task:
        return task
    raise HTTPException(status_code=404)


@router_tasks.post('/video_preview', response_model=TaskVideoPreviewGeneration, status_code=201)
async def create_task_video_preview_generation(video_author_comments: str,
                                               tags: str,
                                               video: UploadFile = File()):
    try:
        video_bytes_io = await upload_file_as_bytes_io(video)
        task = await task_video_preview_gs.create(video_author_comments, tags, video_bytes_io, video.filename)
        return task
    except BaseException as e:
        logger.exception(e)
        raise 500


@router_tasks.post('/avatar', response_model=TaskAvatarGeneration, status_code=201)
async def create_task_avatar_generation(
        avatar_description: str,
        photo: UploadFile = File()):
    input_task = InputTaskAvatarGeneration(avatar_description=avatar_description)
    task = await task_avatar_gs.create(input_task, photo)
    return task


@router_tasks.post('/channel_banner', response_model=TaskChannelBannerGeneration, status_code=201)
async def create_task_channel_banner_generation(channel_banner_description: str):
    input_task = InputTaskChannelBannerGeneration(channel_banner_description=channel_banner_description)
    task = await task_channel_banner_gs.create(input_task)
    return task


@router_tasks.on_event('startup')
async def startup():
    db_url = get_db_url(db_config.driver,
                        db_config.host,
                        db_config.port,
                        db_config.user,
                        db_config.password,
                        db_config.name)
    engine = create_async_engine(db_url)
    async_session = async_sessionmaker(engine, expire_on_commit=False)
    async_session_users = [task_video_preview_gs, task_avatar_gs, task_channel_banner_gs, task_gs, task_image_s]
    for async_session_user in async_session_users:
        async_session_user.set_async_session(async_session)

    await rabbit_producer.start()
    await rabbit_consumer.start()
    task_updates_consumers = [task_video_preview_generation_updates_consumer, task_avatar_generation_updates_consumer,
                              task_channel_banner_generation_updates_consumer]
    for task_updates_consumer in task_updates_consumers:
        await task_updates_consumer.setup()


@router_tasks.on_event('shutdown')
async def shutdown():
    await rabbit_producer.stop()
    await rabbit_consumer.stop()
