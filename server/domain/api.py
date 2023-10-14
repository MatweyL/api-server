import asyncio
from typing import Union

from fastapi import APIRouter, HTTPException
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from server.adapters.inbound.consumer.conifg import rabbit_consumer_config
from server.adapters.inbound.consumer.mock import RabbitConsumerMock
from server.adapters.inbound.consumer.rabbit import RabbitConsumer
from server.adapters.outbound.producer.conifg import rabbit_producer_config
from server.adapters.outbound.producer.rabbit import RabbitProducer
from server.common.config import db_config
from server.common.utils import get_db_url
from server.domain.config import task_producer_config, task_updates_consumer_config
from server.domain.schemas import InputTaskVideoPreviewGeneration, InputTaskAvatarGeneration, \
    InputTaskChannelBannerGeneration
from server.domain.schemas.main import TaskGeneration, TaskVideoPreviewGeneration, TaskAvatarGeneration, \
    TaskChannelBannerGeneration
from server.domain.services import TaskVideoPreviewGenerationService, TaskGenerationService, TaskGenerationFacade, \
    TaskImageService
from server.domain.services_mock import TaskGenerationServiceMock
from server.domain.task_producer import TaskGenerationProducer
from server.domain.task_updates_consumer import TaskGenerationUpdatesConsumer

router_tasks = APIRouter(prefix='/tasks')
task_gs_mock = TaskGenerationServiceMock()
background_tasks = set()

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
task_video_preview_generation_producer = TaskGenerationProducer(rabbit_producer,
                                                                task_producer_config.video_preview_queue_name)
task_video_preview_gs = TaskVideoPreviewGenerationService(task_video_preview_generation_producer)
task_gs = TaskGenerationService()
task_image_s = TaskImageService()
task_video_preview_generation_updates_consumer = TaskGenerationUpdatesConsumer(rabbit_consumer,
                                                                               task_updates_consumer_config.video_preview_queue_name,
                                                                               task_gs, task_image_s)

task_facade = TaskGenerationFacade(task_gs, task_video_preview_gs, task_image_s)


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
async def create_task_video_preview_generation(task: InputTaskVideoPreviewGeneration):
    task = await task_video_preview_gs.create(task)
    return task


@router_tasks.post('/avatar', response_model=TaskGeneration, status_code=201)
async def create_task_avatar_generation(task: InputTaskAvatarGeneration):
    task = task_gs_mock.generate_task(task)
    return task


@router_tasks.post('/channel_banner', response_model=TaskGeneration, status_code=201)
async def create_task_channel_banner_generation(task: InputTaskChannelBannerGeneration):
    task = task_gs_mock.generate_task(task)
    return task


@router_tasks.on_event('startup')
async def startup():
    task = asyncio.create_task(task_gs_mock.periodic_tasks_statuses_changing())
    background_tasks.add(task)
    task.add_done_callback(background_tasks.discard)
    db_url = get_db_url(db_config.driver,
                        db_config.host,
                        db_config.port,
                        db_config.user,
                        db_config.password,
                        db_config.name)
    engine = create_async_engine(db_url)
    async_session = async_sessionmaker(engine, expire_on_commit=False)
    async_session_users = [task_video_preview_gs, task_gs, task_image_s]
    for async_session_user in async_session_users:
        async_session_user.set_async_session(async_session)

    await rabbit_producer.start()
    await rabbit_consumer.start()
    await task_video_preview_generation_updates_consumer.setup()


@router_tasks.on_event('shutdown')
async def shutdown():
    await rabbit_producer.stop()
    await rabbit_consumer.stop()
