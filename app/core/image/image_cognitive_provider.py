from abc import ABC, abstractmethod
from typing import List


class ImageCognitiveProvider(ABC):
    @abstractmethod
    async def describe(self, url: str, language: str = "en") -> str:
        ...