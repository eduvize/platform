import uuid
import json
from datetime import datetime
from typing import Annotated, Optional

from pydantic import Field, field_serializer, field_validator
from domain.schema.chat import ChatMessageBase, ChatToolCallBase

class ChatToolCallDto(ChatToolCallBase):
    tool_name: str
    json_arguments: Annotated[dict, Field(serialization_alias="arguments")]

    @field_validator("json_arguments", mode="plain")
    def serialize_json_arguments(cls, value):
        if isinstance(value, str):
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                raise ValueError("Invalid JSON")    
        
        return value

class ChatMessageDto(ChatMessageBase):
    id: uuid.UUID
    is_user: bool
    content: Optional[str] = None
    tool_calls: list[ChatToolCallDto] = []
    created_at_utc: datetime