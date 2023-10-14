from abc import abstractmethod

from server.domain.schemas import TaskGeneration


class WorkerInterface:

    @abstractmethod
    async def generate(self, task: TaskGeneration) -> TaskGeneration:
        pass
