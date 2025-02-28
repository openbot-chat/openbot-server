from abc import ABC, abstractmethod
from .context import LoaderContext


class DatasourceLoader(ABC):
    @abstractmethod
    async def load(self, context: LoaderContext) -> None:
        ...