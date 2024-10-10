import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import uuid
from app.services.chat_service import ChatService
from domain.schema.chat.chat_message import ChatMessage
from domain.dto.ai.completion_chunk import CompletionChunk
from domain.dto.chat.chat_message import ChatMessageDto
from domain.enums.chat_enums import PromptType
from ai.common.base_message import BaseChatMessage, ChatRole
from typing import AsyncGenerator

# Test data
user_id = "user123"
session_id = uuid.uuid4()
resource_id = uuid.uuid4()
prompt_type = PromptType.LESSON
message = "This is a test message."
mock_lesson = MagicMock()

@pytest.fixture
def chat_service():
    user_service = AsyncMock()
    chat_repository = AsyncMock()
    course_repository = AsyncMock()
    return ChatService(user_service=user_service, chat_repository=chat_repository, course_repository=course_repository)

@pytest.mark.asyncio
async def test_create_session(chat_service):
    """
    Test creating a chat session
    1. Should call user_service.get_user to validate the user.
    2. Should call chat_repository.create_chat_session and return session ID.
    """
    mock_session = MagicMock(id=session_id)
    
    # Mock the user service and repository methods
    chat_service.user_service.get_user.return_value = MagicMock(id=user_id)
    chat_service.chat_repository.create_chat_session.return_value = mock_session
    
    result = await chat_service.create_session(user_id=user_id, prompt_type=prompt_type, resource_id=resource_id)
    
    chat_service.user_service.get_user.assert_awaited_once_with("id", user_id)
    chat_service.chat_repository.create_chat_session.assert_awaited_once_with(
        user_id=user_id,
        prompt_type=prompt_type.value,
        resource_id=resource_id
    )
    
    assert result == session_id

@pytest.mark.asyncio
async def test_get_history(chat_service):
    """
    Test retrieving chat history for a session.
    1. Should call user_service.get_user to validate the user.
    2. Should return the chat message history as ChatMessageDto list.
    """
    mock_messages = [MagicMock(spec=ChatMessage, content="Hello", is_user=True, session_id=session_id, id=uuid.uuid4())]
    
    chat_service.user_service.get_user.return_value = MagicMock(id=user_id)
    chat_service.chat_repository.get_chat_messages.return_value = mock_messages
    
    result = await chat_service.get_history(user_id=user_id, session_id=session_id)
    
    chat_service.user_service.get_user.assert_awaited_once_with("id", user_id)
    chat_service.chat_repository.get_chat_messages.assert_awaited_once_with(session_id)
    
    assert len(result) == len(mock_messages)
    assert isinstance(result[0], ChatMessageDto)

@pytest.mark.asyncio
@patch("app.services.chat_service.ChatService.get_prompt_generator")
async def test_get_response(mock_get_prompt_generator, chat_service):
    """
    Test getting chat response from AI.
    1. Should call user_service.get_user to validate the user.
    2. Should iterate over the response generator and yield CompletionChunks.
    3. Should add both user and AI messages to the chat repository.
    """
    async def mock_generator() -> AsyncGenerator[CompletionChunk, None]:
        yield CompletionChunk(message_id="message_id", text="chunk1")

    mock_get_prompt_generator.return_value = mock_generator()

    chat_service.user_service.get_user = AsyncMock(return_value=MagicMock(id=user_id))
    chat_service.chat_repository.get_session = AsyncMock(return_value=MagicMock(id=session_id))
    chat_service._add_message = AsyncMock()
    
    response = []
    async for chunk in chat_service.get_response(user_id=user_id, session_id=session_id, message=message):
        response.append(chunk)
    
    chat_service.user_service.get_user.assert_awaited_once_with("id", user_id, ["profile.*"])
    chat_service.chat_repository.get_session.assert_awaited_once_with(session_id)
    
    assert len(response) == 1
    assert response[0].message_id == "message_id"
    assert response[0].text == "chunk1"

@pytest.mark.asyncio
async def test_add_message(chat_service):
    """
    Test adding a message to a chat session.
    1. Should add a user or agent message to the chat repository.
    2. Should add tool calls if they exist.
    """
    chat_service.chat_repository.add_chat_message.return_value = MagicMock(id=uuid.uuid4())
    chat_service.chat_repository.add_tool_message = AsyncMock()
    
    await chat_service._add_message(session_id=session_id, is_user=True, message="User message")
    
    chat_service.chat_repository.add_chat_message.assert_awaited_once_with(session_id=session_id, is_user=True, content="User message")

    # Test with tool calls
    tool_calls = [MagicMock(id="tool1", name="test_tool", arguments="{}", result="result")]
    await chat_service._add_message(session_id=session_id, is_user=False, message="Agent message", tool_calls=tool_calls)

@pytest.mark.asyncio
async def test_get_chat_messages(chat_service):
    """
    Test converting chat message records into a representation for the AI.
    """
    mock_records = [
        MagicMock(is_user=True, content="User message", tool_calls=[]),
        MagicMock(is_user=False, content="Agent message", tool_calls=[
            MagicMock(id="tool1", tool_name="test_tool", json_arguments="{}", result="result")
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