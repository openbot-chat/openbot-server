from fastapi import HTTPException
from typing import Dict
from core.image import ImageCognitiveProvider
from core.image.providers.azure import AzureImageCognitiveProvider



class ImageCognitiveManager:
    def __init__(self):
        self.providers: Dict[str, ImageCognitiveProvider] = {
            "azure": AzureImageCognitiveProvider(),
        }

    async def describe(self, provider: str, url: str, language: str = "en") -> str:
        # load provider with credentials
        p = self.providers.get(provider)
        if not p:
            raise HTTPException(status_code=400, detail={'error': f"Image Cognitive Provider: {provider} not found"})
        return await p.describe(url, language)