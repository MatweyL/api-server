from typing import Optional

from sqlalchemy import update, select
from sqlalchemy.ext.asyncio import AsyncSession

from service.domain.converters import map_schema_to_model, map_model_to_schema, map_model_with_existing_schema
from service.domain.models import TaskGenerationModel, TaskVideoPreviewGenerationModel
from service.domain.schemas import TaskStatus, TaskGeneration, TaskVideoPreviewGeneration


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
    async def update_video_text(task_uid: str, video_text: str, session: AsyncSession):
        update_stmt = update(TaskVideoPreviewGenerationModel) \
            .where(TaskVideoPreviewGenerationModel.task_uid == task_uid) \
            .values(video_text=video_text)
        await session.execute(update_stmt)

    @staticmethod
    async def get(task_uid: str, session: AsyncSession) -> TaskVideoPreviewGeneration:
        task_generation = await TaskGenerationCRUD.get(task_uid, session)
        select_stmt = select(TaskVideoPreviewGenerationModel)\
            .where(TaskVideoPreviewGenerationModel.task_uid == task_uid)
        task_video_preview_generation_model = (await session.execute(select_stmt)).scalar_one_or_none()
        task_video_preview_generation_schema = map_model_with_existing_schema(task_video_preview_generation_model,
                                                                              task_generation,
                                                                              TaskVideoPreviewGeneration)
        return task_video_preview_generation_schema
