import uuid
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.services.playground_service import PlaygroundService

# Sample data
user_id = "user123"
session_id = "session123"
token = "mocked_jwt_token"

@pytest.fixture
def playground_service():
    playground_repo = MagicMock()
    return PlaygroundService(playground_repo=playground_repo)

@pytest.mark.asyncio
@patch("app.services.playground_service.create_token", autospec=True)
@patch("app.services.playground_service.get_playground_token_secret", autospec=True)
async def test_create_playground(
    mock_get_playground_token_secret, 
    mock_create_token, 
    playground_service
):
    """
    Test create_playground method:
    1. Should create a new playground session.
    2. Should generate a JWT token with the session ID and user ID.
    3. Should return the session ID and token.
    """
    # Mock repository method
    playground_service.playground_repo.create_playground_session = AsyncMock(return_value=session_id)
    
    # Mock the external function to get the token secret
    mock_get_playground_token_secret.return_value = "mocked_secret"
    
    # Mock JWT token creation
    mock_create_token.return_value = token
    
    env_id = uuid.uuid4()
    
    result = await playground_service.create_playground_session(user_id=user_id, environment_id=env_id)
    
    # Assertions
    playground_service.playground_repo.create_playground_session.assert_awaited_once_with(environment_id=env_id, hostname_override=None)
    mock_get_playground_token_secret.assert_called_once()
    mock_create_token.assert_called_once_with(
        data={"session_id": session_id, "environment_id": str(env_id), "user_id": user_id},
        secret="mocked_secret",
        expiration_minutes=5
    )
    
    assert result == (session_id, token)

@pytest.mark.asyncio
@patch("app.services.playground_service.create_token", autospec=True)
@patch("app.services.playground_service.get_playground_token_secret", autospec=True)
@patch("app.services.playground_service.get_playground_session_override", autospec=True)
async def test_create_playground_session_override(mock_session_id_override, mock_get_playground_token_secret, mock_create_token, playground_service):
    """
    Test create_playground method when session ID override is set:
    1. Should not create a new record in the repository.
    2. Should generate a JWT token with the session ID and user ID.
    3. Should return the session ID and token. Session ID should be the overridden value.
    """
    # Mock repository method
    playground_service.playground_repo.create_playground_session = AsyncMock(return_value="incorrect_session_id")
    
    # Mock the external function to get the token secret
    mock_get_playground_token_secret.return_value = "mocked_secret"
    
    # Mock the override
    mock_session_id_override.return_value = session_id
    
    # Mock JWT token creation
    mock_create_token.return_value = token
    
    env_id = uuid.uuid4()
    
    result = await playground_service.create_playground_session(user_id=user_id, environment_id=env_id)
    
    # Assertions
    playground_service.playground_repo.create_playground_session.assert_not_called()
    mock_get_playground_token_secret.assert_called_once()
    mock_create_token.assert_called_once_with(
        data={"session_id": session_id, "environment_id": str(env_id), "user_id": user_id},
        secret="mocked_secret",
        expiration_minutes=5
    )
    
    assert result == (session_id, token)