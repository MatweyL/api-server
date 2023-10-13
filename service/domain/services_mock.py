import asyncio
from random import randint, choices
from typing import Dict, Type, Optional

from service.domain.schemas import InputTaskGeneration, TaskStatus, TaskType
from service.domain.schemas.service import TaskGeneration, TaskAvatarGeneration, TaskVideoPreviewGeneration, \
    TaskChannelBannerGeneration
from service.domain.utils import generate_uid

random_urls_list = [
    "https://cs14.pikabu.ru/post_img/2023/10/11/5/1697006554257248407.jpg",
    "https://cs14.pikabu.ru/post_img/2023/10/11/5/1697006554228392263.jpg",
    "https://cs13.pikabu.ru/post_img/2023/10/11/5/1697006553295118337.jpg",
    "https://cs13.pikabu.ru/post_img/2023/10/11/5/1697006553261577579.jpg",
    "https://cs13.pikabu.ru/post_img/2023/10/11/5/1697006553229236883.jpg",
    "https://cs14.pikabu.ru/post_img/2023/10/11/5/1697006552293960840.jpg",
    "https://cs13.pikabu.ru/post_img/2023/10/11/5/1697006552264521988.jpg",
    "https://cs14.pikabu.ru/post_img/2023/10/10/5/1696923600269158742.jpg",
    "https://cs14.pikabu.ru/post_img/2023/10/10/5/1696923600269158742.jpg",
    "https://cs14.pikabu.ru/post_img/2023/10/11/6/1697013759135914301.jpg",
    "https://cs13.pikabu.ru/post_img/2023/10/11/6/1697013862187095843.jpg"
]

task_running_statuses = {
    TaskStatus.TEXT_EXTRACTION_WAITING: TaskStatus.TEXT_EXTRACTION_RUNNING,
    TaskStatus.TEXT_EXTRACTION_RUNNING: TaskStatus.TEXT_EXTRACTION_FINISHED,
    TaskStatus.TEXT_EXTRACTION_FINISHED: TaskStatus.GENERATION_WAITING,
    TaskStatus.GENERATION_WAITING: TaskStatus.GENERATION_RUNNING,
    TaskStatus.GENERATION_RUNNING: TaskStatus.GENERATION_FINISHED
}


class TaskGenerationServiceMock:

    def __init__(self):
        self._tasks: Dict[str, TaskGeneration] = {}
        self._types_schemas: Dict[TaskType, Type[TaskGeneration]] = {
            TaskType.VIDEO_PREVIEW_GENERATION: TaskVideoPreviewGeneration,
            TaskType.AVATAR_GENERATION: TaskAvatarGeneration,
            TaskType.CHANNEL_BANNER_GENERATION: TaskChannelBannerGeneration
        }

    def generate_task(self, input_task: InputTaskGeneration) -> TaskGeneration:
        uid = generate_uid()
        if input_task.task_type == TaskType.VIDEO_PREVIEW_GENERATION:
            status = TaskStatus.TEXT_EXTRACTION_WAITING
        else:
            status = TaskStatus.GENERATION_WAITING
        task = self._types_schemas[input_task.task_type](task_uid=uid, task_status=status, **input_task.model_dump(),
                                                         task_images_urls=[])

        self._tasks[uid] = task
        return task

    def get_task(self, uid: str) -> Optional[TaskGeneration]:
        try:
            task = self._tasks[uid]
        except KeyError:
            pass
        else:
            return task

    async def periodic_tasks_statuses_changing(self):
        while True:
            await asyncio.sleep(randint(1, 10))
            for task in self._tasks.values():
                previous_task_status = task.task_status
                try:
                    task.task_status = task_running_statuses[previous_task_status]
                except KeyError:
                    pass
                else:
                    if previous_task_status == TaskStatus.GENERATION_RUNNING:
                        task.task_images_urls = choices(random_urls_list, k=randint(1, 2))
