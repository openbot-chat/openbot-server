from models.chat import ChatMessage
from models.conversation import ConversationSchema
from abc import ABC, abstractmethod
from typing import List

class MessageProcessor(ABC):
    @abstractmethod
    async def process(self, conversation: ConversationSchema, message: ChatMessage):
        ...


class MessageRoutine:
    def __init__(self):
        self.processors: List[MessageProcessor] = []

    def add_processor(self, processor: MessageProcessor):
        self.processors.append(processor)

    def remove_processor(self, processor: MessageProcessor):
        self.processors.remove(processor)

    async def process(self, conversation: ConversationSchema, message: ChatMessage):
        for processor in self.processors:
            await processor.process(conversation, message)