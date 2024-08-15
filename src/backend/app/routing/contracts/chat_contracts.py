from typing import Optional
import uuid
from pydantic import BaseModel

class ChatSessionReference(BaseModel):
    curriculum_id: Optional[uuid.UUID] = None
    lesson_id: Optional[uuid.UUID] = None
    exercise_id: Optional[uuid.UUID] = None

class SendChatMessage(ChatSessionReference):
    message: str