from typing import List
from models.chat import ChatMessage
from models.conversation import ConversationSchema
from .message_routine import MessageProcessor
import logging
from core.image.image_cognitive_manager import ImageCognitiveManager


class ImageTranscribeProcessor(MessageProcessor):
    def __init__(self, image_cognitive_manager: ImageCognitiveManager):
        self.image_cognitive_manager = image_cognitive_manager

    async def process(
        self,
        conversation: ConversationSchema,
        message: ChatMessage,
    ):
        if message.text is not None and len(message.text) > 0:
            return

        images = message.images
        if images is None or len(images) == 0:
            return

        texts: List[str] = []

        for image in images:
            description = await self.image_cognitive_manager.describe('azure', image.url)
            text = f"""this is a image: 
            url: {image.url}
            content: {description}

            """

            texts.append(text)
            logging.debug(f"ImageCognitiveManager describe Message, url: {image.url} -> text: {description}")

        message.text = "\n".join(texts)