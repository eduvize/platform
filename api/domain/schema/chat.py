from common.database import Context
from sqlalchemy import TIMESTAMP, Boolean, Column, ForeignKey, Integer, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship
import uuid

class ChatSession(Context):
    __tablename__ = "chat_sessions"
    
    id                          = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id                     = Column(PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    curriculum_id               = Column(PG_UUID(as_uuid=True), ForeignKey("curriculums.id"), nullable=True)
    lesson_id                   = Column(PG_UUID(as_uuid=True), ForeignKey("lessons.id"), nullable=True)
    exercise_id                 = Column(PG_UUID(as_uuid=True), ForeignKey("exercises.id"), nullable=True)
    created_at_utc              = Column(TIMESTAMP, nullable=False, default='now()')
    
    user                        = relationship("User", back_populates="chat_sessions", uselist=False)
    messages                    = relationship("ChatMessage", back_populates="session")
    
class ChatMessage(Context):
    __tablename__ = "chat_messages"
    
    id                          = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id                  = Column(PG_UUID(as_uuid=True), ForeignKey("chat_sessions.id"), nullable=False)
    is_user                     = Column(Boolean, nullable=False)
    content                     = Column(Text, nullable=False)
    created_at_utc              = Column(TIMESTAMP, nullable=False, default='now()')
    
    session                     = relationship("ChatSession", back_populates="messages", uselist=False)
    tool_calls                  = relationship("ChatToolCall", back_populates="message")
    
class ChatToolCall(Context):
    __tablename__ = "chat_tool_calls"
    
    id                          = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    message_id                  = Column(PG_UUID(as_uuid=True), ForeignKey("chat_messages.id"), nullable=False)
    tool_call_id                = Column(Text, nullable=False)
    tool_name                   = Column(Text, nullable=False)
    json_arguments              = Column(Text, nullable=False)
    result                      = Column(Text, nullable=False)
    
    message                     = relationship("ChatMessage", back_populates="tool_calls", uselist=False)