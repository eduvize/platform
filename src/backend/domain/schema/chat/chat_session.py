import uuid
from datetime import datetime
from typing import Optional
from sqlmodel import Field, Relationship, SQLModel
import domain.schema as schema

class ChatSessionBase(SQLModel):
    curriculum_id: Optional[uuid.UUID]      = Field(default=None, foreign_key="curriculums.id")
    lesson_id: Optional[uuid.UUID]          = Field(default=None, foreign_key="lessons.id")
    exercise_id: Optional[uuid.UUID]        = Field(default=None, foreign_key="exercises.id")
    created_at_utc: datetime                = Field(default_factory=datetime.utcnow, nullable=False)

class ChatSession(ChatSessionBase, table=True):
    __tablename__ = "chat_sessions"
    
    id: uuid.UUID                                           = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID                                      = Field(default=None, foreign_key="users.id")
    messages: list["schema.chat.chat_message.ChatMessage"]  = Relationship(back_populates="chat_session")