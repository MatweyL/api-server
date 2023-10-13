import asyncio
from typing import Union, Optional

from fastapi import APIRouter, HTTPException
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from service.common.config import db_config
from service.common.logs import logger
from service.common.utils import get_db_url
from service.domain.schemas import InputTaskVideoPreviewGeneration, InputTaskAvatarGeneration, \
    InputTaskChannelBannerGeneration
from service.domain.schemas.service import TaskGeneration, TaskVideoPreviewGeneration, TaskAvatarGeneration, \
    TaskChannelBannerGeneration
from service.domain.services import TaskVideoPreviewGenerationService, TaskGenerationService
from service.domain.services_mock import TaskGenerationServiceMock
from service.domain.task_producer import TaskProducerMock

router_tasks = APIRouter(prefix='/tasks')
task_generation_service = TaskGenerationServiceMock()
background_tasks = set()

task_producer = TaskProducerMock()
task_video_preview_gs = TaskVideoPreviewGenerationService(task_producer)
task_gs = TaskGenerationService()


@router_tasks.get('/', response_model=Union[TaskVideoPreviewGeneration,
                                            TaskAvatarGeneration,
                                            TaskChannelBannerGeneration],
                  status_code=200)
async def get_task_by_uid(uid: str):
    task = task_generation_service.get_task(uid)
    if task:
        return task
    raise HTTPException(status_code=404)


@router_tasks.post('/video_preview', response_model=TaskGeneration, status_code=201)
async def create_task_video_preview_generation(task: InputTaskVideoPreviewGeneration):
    task = await task_video_preview_gs.create(task)
    return task


@router_tasks.post('/avatar', response_model=TaskGeneration, status_code=201)
async def create_task_avatar_generation(task: InputTaskAvatarGeneration):
    task = task_generation_service.generate_task(task)
    return task


@router_tasks.post('/channel_banner', response_model=TaskGeneration, status_code=201)
async def create_task_channel_banner_generation(task: InputTaskChannelBannerGeneration):
    task = task_generation_service.generate_task(task)
    return task


@router_tasks.on_event('startup')
async def startup():
    task = asyncio.create_task(task_generation_service.periodic_tasks_statuses_changing())
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
    task_video_preview_gs.set_async_session(async_session)
    task_gs.set_async_session(async_session)
    try:
        tg = await task_video_preview_gs.get('5d552bde-fc38-4f62-a25a-245036f33da4')
        print(tg)
    except BaseException as e:
        logger.exception(e)