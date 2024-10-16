import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import uuid
from app.services.chat_service import ChatService
from domain.schema.chat.chat_message import ChatMessage
from domain.schema.chat.chat_session import ChatSession
from domain.schema.instructors.instructor import Instructor
from domain.dto.ai.completion_chunk import CompletionChunk
from domain.dto.chat.chat_message import ChatMessageDto
from domain.enums.chat_enums import PromptType
from ai.common.base_message import BaseChatMessage, ChatRole
from typing import AsyncGenerator

# Test data
user_id = str(uuid.uuid4())
session_id = uuid.uuid4()
resource_id = uuid.uuid4()
instructor_id = uuid.uuid4()
prompt_type = PromptType.LESSON
message = "This is a test message."
mock_lesson = MagicMock()

@pytest.fixture
def chat_service():
    user_service = AsyncMock()
    instructor_service = AsyncMock()
    chat_repository = AsyncMock()
    course_repository = AsyncMock()
    return ChatService(
        user_service=user_service,
        instructor_service=instructor_service,
        chat_repository=chat_repository,
        course_repository=course_repository
    )

@pytest.mark.asyncio
async def test_create_session(chat_service):
    """
    Test creating a chat session
    1. Should call user_service.get_user to validate the user.
    2. Should call instructor_service.get_user_instructor to get the instructor.
    3. Should call chat_repository.create_chat_session and return the session.
    """
    mock_user = MagicMock(id=user_id)
    mock_session = MagicMock(spec=ChatSession, id=session_id)
    
    chat_service.user_service.get_user.return_value = mock_user
    chat_service.chat_repository.create_chat_session.return_value = mock_session
    
    result = await chat_service.create_session(user_id=user_id)
    
    chat_service.user_service.get_user.assert_awaited_once_with("id", user_id)
    chat_service.chat_repository.create_chat_session.assert_awaited_once_with(
        user_id=user_id
    )
    
    assert result == mock_session

@pytest.mark.asyncio
async def test_get_history(chat_service):
    """
    Test retrieving chat history for a session.
    1. Should call user_service.get_user to validate the user.
    2. Should return the chat message history as ChatMessageDto list.
    """
    mock_user = MagicMock(id=user_id)
    mock_messages = [MagicMock(spec=ChatMessage, content="Hello", is_user=True, session_id=session_id, id=uuid.uuid4(), user_id=user_id, instructor_id=None)]
    
    chat_service.user_service.get_user.return_value = mock_user
    chat_service.chat_repository.get_chat_messages.return_value = mock_messages
    
    result = await chat_service.get_history(user_id=user_id, session_id=session_id)
    
    chat_service.user_service.get_user.assert_awaited_once_with("id", user_id)
    chat_service.chat_repository.get_chat_messages.assert_awaited_once_with(session_id)
    
    assert len(result) == len(mock_messages)
    assert isinstance(result[0], ChatMessageDto)

@pytest.mark.asyncio
async def test_add_message(chat_service):
    """
    Test adding a message to a chat session.
    1. Should add a user or agent message to the chat repository.
    2. Should add tool calls if they exist.
    """
    mock_message = MagicMock(id=uuid.uuid4())
    chat_service.chat_repository.add_chat_message.return_value = mock_message
    chat_service.chat_repository.add_tool_message = AsyncMock()
    
    await chat_service._add_message(session_id=session_id, sender_id=user_id, is_user=True, message="User message")
    
    chat_service.chat_repository.add_chat_message.assert_awaited_once_with(
        session_id=session_id,
        is_user=True,
        content="User message",
        sender_id=user_id
    )

@pytest.mark.asyncio
async def test_get_chat_messages(chat_service):
    """
    Test converting chat message records into a representation for the AI.
    """
    mock_records = [
        MagicMock(is_user=True, content="User message", tool_calls=[]),
        MagicMock(is_user=False, content="Agent message", tool_calls=[
            MagicMock(tool_call_id="tool1", tool_name="test_tool", json_arguments="{}", result="result")
        ])
    ]
    
    result = chat_service._get_chat_messages(mock_records)
    
    assert len(result) == 2
    assert result[0].role == ChatRole.USER
    assert result[0].message == "User message"
    assert result[1].role == ChatRole.AGENT
    assert result[1].message == "Agent message"
    assert len(result[1].tool_calls) == 1
    assert result[1].tool_calls[0].id == "tool1"
    assert result[1].tool_calls[0].name == "test_tool"