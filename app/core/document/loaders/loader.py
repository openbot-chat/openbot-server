from abc import ABC, abstractmethod
from vectorstore.models import Document
from typing import List


class DocumentLoader(ABC):
    @abstractmethod
    async def load(self) -> List[Document]:
        ...