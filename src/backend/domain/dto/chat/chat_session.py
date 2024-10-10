from datetime import datetime
import uuid
from domain.schema.chat import ChatSessionBase

class ChatSessionDto(ChatSessionBase):
    id: uuid.UUID
    instructor_id: uuid.UUID
    created_at_utc: datetime