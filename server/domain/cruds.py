from typing import Optional, List

from sqlalchemy import update, select
from sqlalchemy.ext.asyncio import AsyncSession

from server.domain.utils import map_schema_to_model, map_model_to_schema, map_model_with_existing_schema
from server.domain.models import TaskGenerationModel, TaskVideoPreviewGenerationModel, TaskImageModel, \
    TaskAvatarGenerationModel, TaskChannelBannerGenerationModel
from server.domain.schemas import TaskStatus, TaskGeneration, TaskVideoPreviewGeneration, TaskImage, \
    TaskAvatarGeneration, TaskChannelBannerGeneration


class TaskGenerationCRUD:

    @staticmethod
    async def create(task_schema: TaskGeneration, session: AsyncSession):
        task_generation_model = map_schema_to_model(task_schema, TaskGenerationModel)
        session.add(task_generation_model)

    @staticmethod
    async def update_status(task_uid: str, new_task_status: TaskStatus, session: AsyncSession):
        update_stmt = update(TaskGenerationModel) \
            .where(TaskGenerationModel.task_uid == task_uid) \
            .values(task_status=new_task_status)
        await session.execute(update_stmt)

    @staticmethod
    async def get(task_uid: str, session: AsyncSession) -> Optional[TaskGeneration]:
        select_stmt = select(TaskGenerationModel).where(TaskGenerationModel.task_uid == task_uid)

        task_generation_model = (await session.execute(select_stmt)).scalar_one_or_none()
        if task_generation_model:
            return map_model_to_schema(task_generation_model, TaskGeneration)


class TaskVideoPreviewGenerationCRUD:

    @staticmethod
    async def create(task_schema: TaskVideoPreviewGeneration, session: AsyncSession):
        task = map_schema_to_model(task_schema, TaskVideoPreviewGenerationModel)
        session.add(task)

    @staticmethod
    async def get(task_uid: str, session: AsyncSession) -> TaskVideoPreviewGeneration:
        task_generation = await TaskGenerationCRUD.get(task_uid, session)
        select_stmt = select(TaskVideoPreviewGenerationModel) \
            .where(TaskVideoPreviewGenerationModel.task_uid == task_uid)
        task_video_preview_generation_model = (await session.execute(select_stmt)).scalar_one_or_none()
        task_video_preview_generation_schema = map_model_with_existing_schema(task_video_preview_generation_model,
                                                                              task_generation,
                                                                              TaskVideoPreviewGeneration)
        return task_video_preview_generation_schema


class TaskImageCRUD:

    @staticmethod
    async def get_all(task_uid: str, session: AsyncSession) -> List[TaskImage]:
        select_stmt = select(TaskImageModel) \
            .where(TaskImageModel.task_uid == task_uid)
        tasks_images_models = (await session.execute(select_stmt)).scalars()
        tasks_images_schemas = [map_model_to_schema(task_image_model, TaskImage)
                                for task_image_model in tasks_images_models]
        return tasks_images_schemas

    @staticmethod
    async def create_all(tasks_images: List[TaskImage], session: AsyncSession):
        tasks_images_models = [map_schema_to_model(task_image, TaskImageModel)
                               for task_image in tasks_images]
        for task_image_model in tasks_images_models:
            session.add(task_image_model)


class TaskAvatarGenerationCRUD:

    @staticmethod
    async def create(task_schema: TaskAvatarGeneration, session: AsyncSession):
        task = map_schema_to_model(task_schema, TaskAvatarGenerationModel)
        session.add(task)

    @staticmethod
    async def get(task_uid: str, session: AsyncSession) -> TaskAvatarGeneration:
        task_generation = await TaskGenerationCRUD.get(task_uid, session)
        select_stmt = select(TaskAvatarGenerationModel) \
            .where(TaskAvatarGenerationModel.task_uid == task_uid)
        task_avatar_generation_model = (await session.execute(select_stmt)).scalar_one_or_none()
        task_avatar_generation_schema = map_model_with_existing_schema(task_avatar_generation_model,
                                                                       task_generation,
                                                                       TaskAvatarGeneration)
        return task_avatar_generation_schema


class TaskChannelBannerGenerationCRUD:

    @staticmethod
    async def create(task_schema: TaskChannelBannerGeneration, session: AsyncSession):
        task = map_schema_to_model(task_schema, TaskChannelBannerGenerationModel)
        session.add(task)

    @staticmethod
    async def get(task_uid: str, session: AsyncSession) -> TaskChannelBannerGeneration:
        task_generation = await TaskGenerationCRUD.get(task_uid, session)
        select_stmt = select(TaskChannelBannerGenerationModel) \
            .where(TaskChannelBannerGenerationModel.task_uid == task_uid)
        task_channel_banner_generation_model = (await session.execute(select_stmt)).scalar_one_or_none()
        task_channel_banner_generation_schema = map_model_with_existing_schema(task_channel_banner_generation_model,
                                                                               task_generation,
                                                                               TaskChannelBannerGenerationModel)
        return task_channel_banner_generation_schema
