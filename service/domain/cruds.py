from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from service.domain.converters import map_schema_to_model
from service.domain.models import TaskGenerationModel, TaskVideoPreviewGenerationModel
from service.domain.schemas import TaskStatus, TaskGeneration, TaskVideoPreviewGeneration


class TaskGenerationCRUD:

    @staticmethod
    async def create(task_schema: TaskGeneration, session: AsyncSession):
        task = map_schema_to_model(task_schema, TaskGenerationModel)
        session.add(task)

    @staticmethod
    async def update_status(task_uid: str, new_task_status: TaskStatus, session: AsyncSession):
        update_stmt = update(TaskGenerationModel) \
            .where(TaskGenerationModel.task_uid == task_uid) \
            .values(task_status=new_task_status)
        await session.execute(update_stmt)


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


