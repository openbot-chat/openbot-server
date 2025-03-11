from core.image.image_cognitive_provider import ImageCognitiveProvider
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from msrest.authentication import CognitiveServicesCredentials
import os
from asyncer import asyncify


class AzureImageCognitiveProvider(ImageCognitiveProvider):
    async def describe(self, url: str, language: str = "en") -> str:
        region = os.environ['AZURE_ACCOUNT_REGION']
        key = os.environ['AZURE_ACCOUNT_KEY']

        credentials = CognitiveServicesCredentials(key)
        client = ComputerVisionClient(
            endpoint="https://" + region + ".api.cognitive.microsoft.com/",
            credentials=credentials
        )

        # url = "https://upload.wikimedia.org/wikipedia/commons/thumb/1/12/Broadway_and_Times_Square_by_night.jpg/450px-Broadway_and_Times_Square_by_night.jpg"
        # url = "https://pics3.baidu.com/feed/c2fdfc039245d6881d6db897eef60112d21b2452.jpeg@f_auto?token=ccea8f3bc97778b5738c2a53abf46a90"
        # image_analysis = await asyncify(client.analyze_image)(url, visual_features=[VisualFeatureTypes.description])
        result = await asyncify(client.describe_image)(url, language=language)
        
        text = ''
        for caption in result.captions:
            text = caption.text
            break

        return text