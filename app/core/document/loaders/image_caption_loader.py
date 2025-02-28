from .loader import DocumentLoader
from typing import List
from vectorstore.models import Document
from core.image.image_cognitive_manager import ImageCognitiveManager
from urllib.parse import urlparse
import os


class ImageCaptionLoader(DocumentLoader):
    def __init__(self, url: str):
        self.url = url
    
    async def load(self) -> List[Document]:
        image_cognitive_manager = ImageCognitiveManager()
        description = await image_cognitive_manager.describe('azure', self.url)

        parsed_url = urlparse(self.url)
        key = parsed_url.path[1:]
        file_name, file_extension = os.path.splitext(key)
        file_type = str(file_extension[1:]).lower()

        return [
            Document(
                text=description,
                metadata={
                    "file_type": file_type,
                }
            )
        ]