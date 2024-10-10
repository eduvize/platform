import uuid
from datetime import datetime
from typing import Optional
from sqlmodel import Field, Relationship, SQLModel
import domain.schema as schema

class ChatMessageBase(SQLModel):
    session_id: uuid.UUID               = Field(default=None, foreign_key="chat_sessions.id")
    is_user: bool                       = Field(nullable=False)
    content: Optional[str]              = Field()
    instructor_id: Optional[uuid.UUID]  = Field(nullable=True, foreign_key="instructors.id")
    user_id: Optional[uuid.UUID]        = Field(nullable=True, foreign_key="users.id")
    created_at_utc: datetime            = Field(nullable=False, default_factory=datetime.utcnow)

class ChatMessage(ChatMessageBase, table=True):
    __tablename__ = "chat_messages"
    
    id: uuid.UUID                                           = Field(default_factory=uuid.uuid4, primary_key=True)
    chat_session: "schema.chat.chat_session.ChatSession"    = Relationship(back_populates="messages")
    tool_calls: list["ChatToolCall"]                        = Relationship(back_populates="chat_message")

class ChatToolCallBase(SQLModel):
    tool_name: str                  = Field(nullable=False)
    json_arguments: str             = Field(nullable=False)

class ChatToolCall(ChatToolCallBase, table=True):
    __tablename__ = "chat_tool_calls"
    
    id: uuid.UUID                   = Field(default_factory=uuid.uuid4, primary_key=True)
    message_id: uuid.UUID           = Field(default=None, foreign_key="chat_messages.id")
    tool_call_id: str               = Field(nullable=False)
    result: str                     = Field(nullable=False)
    
    chat_message: "ChatMessage"     = Relationship(back_populates="tool_calls")