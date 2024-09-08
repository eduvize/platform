import pytest
from unittest.mock import AsyncMock, patch
from app.websocket.websocket_server import InvalidJWTToken
import app.websocket.websocket_server as socket_server

@pytest.mark.asyncio
@patch("app.websocket.websocket_server.socket_server", autospec=True)
@patch("app.websocket.websocket_server.decode_token")
@patch("app.websocket.websocket_server.get_key", return_value=None)
@patch("app.websocket.websocket_server.set_key")
async def test_connect_user_success(mock_set_key, mock_get_key, mock_decode_token, mock_socket_server):
    """
    Test a successful connection for a user with a valid token.
    """
    # Mock the decoded token
    mock_decode_token.return_value = {
        "session_id": "session123",
        "user_id": "user456",
    }
    
    mock_get_key.return_value = True

    environment_data = {
        "asgi.scope": {
            "headers": [(b'authorization', b'Bearer valid.token.here')]
        }
    }

    result = await socket_server.connect(sid="user123", environment_data=environment_data)

    assert result is True
    mock_socket_server.enter_room.assert_called_once_with("user123", "session123")
    mock_set_key.assert_called_once()
    mock_socket_server.emit.assert_any_call("user_connected", room="session123")
    mock_socket_server.emit.assert_any_call("instance_connected", room="session123")

@pytest.mark.asyncio
@patch("app.websocket.websocket_server.socket_server", autospec=True)
@patch("app.websocket.websocket_server.decode_token", side_effect=InvalidJWTToken)
async def test_connect_invalid_token(mock_decode_token, mock_socket_server):
    """
    Test connection failure due to an invalid JWT token.
    """
    environment_data = {
        "asgi.scope": {
            "headers": [(b'authorization', b'Bearer invalid.token.here')]
        }
    }

    result = await socket_server.connect(sid="user123", environment_data=environment_data)
    
    assert result is False
    mock_socket_server.enter_room.assert_not_called()

@pytest.mark.asyncio
@patch("app.websocket.websocket_server.socket_server", autospec=True)
@patch("app.websocket.websocket_server.get_key", return_value=None)
@patch("app.websocket.websocket_server.decode_token")
async def test_connect_missing_session_id(mock_decode_token, mock_get_key, mock_socket_server):
    """
    Test connection failure due to missing session ID.
    """
    # Mock the decoded token without a session ID
    mock_decode_token.return_value = {
        "user_id": "user456"
    }

    environment_data = {
        "asgi.scope": {
            "headers": [(b'authorization', b'Bearer valid.token.here')]
        }
    }

    result = await socket_server.connect(sid="user123", environment_data=environment_data)

    assert result is False
    mock_socket_server.enter_room.assert_not_called()

@pytest.mark.asyncio
@patch("app.websocket.websocket_server.socket_server", autospec=True)
async def test_disconnect_user(mock_socket_server):
    """
    Test user disconnection and ensure correct events are triggered.
    """
    mock_session = AsyncMock()
    mock_session.__aenter__.return_value = {
        "session_id": "session123",
        "user_id": "user456"
    }
    
    mock_socket_server.session.return_value = mock_session

    await socket_server.disconnect(sid="user123")

    mock_socket_server.emit.assert_called_once_with("user_disconnected", room="session123")

@pytest.mark.asyncio
@patch("app.websocket.websocket_server.socket_server", autospec=True)
async def test_terminal_input(mock_socket_server):
    """
    Test terminal input event.
    """
    mock_session = AsyncMock()
    mock_session.__aenter__.return_value = {
        "session_id": "session123",
        "user_id": "user456"
    }
    
    mock_socket_server.session.return_value = mock_session
    
    await socket_server.terminal_input(sid="user123", t_input="some command")

    mock_socket_server.emit.assert_called_once_with("terminal_input", "some command", room="session123")

@pytest.mark.asyncio
@patch("app.websocket.websocket_server.socket_server", autospec=True)
async def test_terminal_output(mock_socket_server):
    """
    Test terminal output event.
    """
    mock_session = AsyncMock()
    mock_session.__aenter__.return_value = {
        "session_id": "session123",
        "user_id": "user456"
    }
    
    mock_socket_server.session.return_value = mock_session
    
    await socket_server.terminal_output(sid="user123", output="output text")

    mock_socket_server.emit.assert_called_once_with("terminal_output", "output text", room="session123")

@pytest.mark.asyncio
@patch("app.websocket.websocket_server.socket_server", autospec=True)
async def test_terminal_resize(mock_socket_server):
    """
    Test terminal resize event.
    """
    mock_session = AsyncMock()
    mock_session.__aenter__.return_value = {
        "session_id": "session123",
        "user_id": "user456"
    }
    
    mock_socket_server.session.return_value = mock_session
    
    data = {"rows": 24, "columns": 80}
    await socket_server.terminal_resize(sid="user123", data=data)

    mock_socket_server.emit.assert_called_once_with("terminal_resize", data, room="session123")
