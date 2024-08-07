from typing import Optional
import uuid
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship

class ChatSession(SQLModel, table=True):
    __tablename__ = "chat_sessions"
    
    id: uuid.UUID                           = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID                      = Field(default=None, foreign_key="users.id")
    curriculum_id: Optional[uuid.UUID]      = Field(default=None, foreign_key="curriculums.id")
    lesson_id: Optional[uuid.UUID]          = Field(default=None, foreign_key="curriculum_lessons.id")
    exercise_id: Optional[uuid.UUID]        = Field(default=None, foreign_key="curriculum_exercises.id")
    created_at_utc: datetime                = Field(default_factory=datetime.utcnow, nullable=False)
    
    messages: list["ChatMessage"]           = Relationship(back_populates="chat_session")

class ChatMessage(SQLModel, table=True):
    __tablename__ = "chat_messages"
    
    id: uuid.UUID                       = Field(default_factory=uuid.uuid4, primary_key=True)
    session_id: uuid.UUID               = Field(default=None, foreign_key="chat_sessions.id")
    is_user: bool                       = Field(nullable=False)
    content: Optional[str]              = Field()
    created_at_utc: datetime            = Field(nullable=False, default_factory=datetime.utcnow)
    
    chat_session: "ChatSession"         = Relationship(back_populates="messages")
    tool_calls: list["ChatToolCall"]    = Relationship(back_populates="chat_message")
    
class ChatToolCall(SQLModel, table=True):
    __tablename__ = "chat_tool_calls"
    
    id: uuid.UUID                   = Field(default_factory=uuid.uuid4, primary_key=True)
    message_id: uuid.UUID           = Field(default=None, foreign_key="chat_messages.id")
    tool_call_id: uuid.UUID         = Field(nullable=False)
    tool_name: str                  = Field(nullable=False)
    json_arguments: str             = Field(nullable=False)
    result: str                     = Field(nullable=False)
    
    chat_message: "ChatMessage"     = Relationship(back_populates="tool_calls")