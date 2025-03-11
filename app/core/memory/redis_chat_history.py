import json
import logging
from typing import List, Optional

from langchain.schema import (
    BaseChatMessageHistory,
)
from langchain.schema.messages import BaseMessage, _message_to_dict, messages_from_dict
logger = logging.getLogger(__name__)
from redis.asyncio import Redis
from asyncer import runnify



class RedisChatMessageHistory(BaseChatMessageHistory):
    """Chat message history stored in a Redis database."""

    def __init__(
        self,
        session_id: str,
        redis: Redis,
        key_prefix: str = "message_store:",
        ttl: Optional[int] = None,
    ):
        self.redis = redis
        self.session_id = session_id
        self.key_prefix = key_prefix
        self.ttl = ttl

    @property
    def key(self) -> str:
        """Construct the record key to use"""
        return self.key_prefix + self.session_id

    @property
    def messages(self) -> List[BaseMessage]:  # type: ignore
        """Retrieve the messages from Redis"""

        _items = runnify(self.redis.lrange)(self.key, 0, -1)
        items = [json.loads(m.decode("utf-8")) for m in _items[::-1]]
        messages = messages_from_dict(items)
        return messages

    def add_message(self, message: BaseMessage) -> None:
        """Append the message to the record in Redis"""
        runnify(self.redis.lpush)(self.key, json.dumps(_message_to_dict(message)))
        if self.ttl:
            runnify(self.redis.expire)(self.key, self.ttl)

    def clear(self) -> None:
        """Clear session memory from Redis"""
        runnify(self.redis.delete)(self.key)
