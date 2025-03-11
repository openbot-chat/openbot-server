
from functools import cached_property
from langchain.memory import ConversationBufferMemory
from pydantic import BaseModel
from typing import Dict, Any, List
from models.chat import ChatMessage
from services import ConversationService
from langchain.memory.utils import get_prompt_input_key

class ServiceChatMemory(ConversationBufferMemory, BaseModel):
    conversation_id: str
    conversation_service: ConversationService

    class Config:
        keep_untouched = (cached_property,)

    @cached_property
    def chat_history(self) -> List[ChatMessage]:
        page = await self.conversation_service.list_messages(self.conversation_id)
        return [m for m in page.items]

    @property
    def buffer(self) -> Any:
        return self.chat_history
  
    def save_context(self, inputs: Dict[str, Any], outputs: Dict[str, str]) -> None:
        """Save context from this conversation to buffer."""
        if self.input_key is None:
            prompt_input_key = get_prompt_input_key(inputs, self.memory_variables)
        else:
            prompt_input_key = self.input_key
    
        if self.output_key is None:
            if len(outputs) != 1:
                raise ValueError(f"One output key expected, got {outputs.keys()}")
            output_key = list(outputs.keys())[0]
        else:
            output_key = self.output_key

        self.conversation_service.add_message(ChatMessage(
            role="Human", 
            text=inputs[prompt_input_key]
        ))
        self.conversation_service.add_message(ChatMessage(
            role="AI", 
            text=outputs[output_key]
        ))