from datetime import datetime
from typing import Optional
import uuid
from domain.schema.chat import ChatMessageBase

class ChatMessageDto(ChatMessageBase):
    id: uuid.UUID
    is_user: bool
    content: Optional[str] = None
    created_at_utc: datetime