import asyncio
from typing import Union

from fastapi import APIRouter, HTTPException

from service.domain.schemas import InputTaskVideoPreviewGeneration, InputTaskAvatarGeneration, \
    InputTaskChannelBannerGeneration
from service.domain.schemas.service import TaskGeneration, TaskVideoPreviewGeneration, TaskAvatarGeneration, \
    TaskChannelBannerGeneration
from service.domain.services import TaskGenerationService

router_tasks = APIRouter(prefix='/tasks')
task_generation_service = TaskGenerationService()
background_tasks = set()


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
    task = task_generation_service.generate_task(task)
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
