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
@patch("app.websocket.websocket_server.delete_key", autospec=True)
@patch("app.websocket.websocket_server.get_connection_information", autospec=True)
async def test_disconnect_user(mock_get_conn_info, mock_delete_key, mock_socket_server):
    """
    Test user disconnection and ensure correct events are triggered.
    1. Get the session information using the SID
    2. Emit user_disconnected event to the session room without echoing to the SID
    2. Deletion of the user connected key.
    """
    mock_get_conn_info.return_value = "user", "session123"
    cache_key = socket_server.get_user_connected_cache_key("session123")
    
    await socket_server.disconnect(sid="user123")
    
    mock_get_conn_info.assert_called_once_with("user123")
    mock_socket_server.emit.assert_called_once_with("user_disconnected", room="session123", skip_sid="user123")
    mock_delete_key.assert_called_once_with(cache_key)

@pytest.mark.asyncio
@patch("app.websocket.websocket_server.socket_server", autospec=True)
@patch("app.websocket.websocket_server.get_connection_information", autospec=True)
async def test_terminal_input(mock_get_conn_info, mock_socket_server):
    """
    Test terminal input event.
    """
    mock_get_conn_info.return_value = "user", "session123"
    
    await socket_server.terminal_input(sid="user123", t_input="some command")

    mock_get_conn_info.assert_called_once_with("user123")
    mock_socket_server.emit.assert_called_once_with("terminal_input", "some command", room="session123", skip_sid="user123")

@pytest.mark.asyncio
@patch("app.websocket.websocket_server.socket_server", autospec=True)
@patch("app.websocket.websocket_server.get_connection_information", autospec=True)
async def test_terminal_output(mock_get_conn_info, mock_socket_server):
    """
    Test terminal output event.
    """
    mock_get_conn_info.return_value = "instance", "session123"
    
    await socket_server.terminal_output(sid="instance123", output="output text")

    mock_get_conn_info.assert_called_once_with("instance123")
    mock_socket_server.emit.assert_called_once_with("terminal_output", "output text", room="session123", skip_sid="instance123")

@pytest.mark.asyncio
@patch("app.websocket.websocket_server.socket_server", autospec=True)
@patch("app.websocket.websocket_server.get_connection_information", autospec=True)
async def test_terminal_resize(mock_get_conn_info, mock_socket_server):
    """
    Test terminal resize event.
    """
    mock_get_conn_info.return_value = "user", "session123"
    
    data = {"rows": 24, "columns": 80}
    await socket_server.terminal_resize(sid="user123", data=data)

    mock_get_conn_info.assert_called_once_with("user123")
    mock_socket_server.emit.assert_called_once_with("terminal_resize", data, room="session123", skip_sid="user123")

@pytest.mark.asyncio
@patch("app.websocket.websocket_server.socket_server", autospec=True)
@patch("app.websocket.websocket_server.get_connection_information", autospec=True)
async def test_create(mock_get_conn_info, mock_socket_server):
    """
    Test create event.
    """
    mock_get_conn_info.return_value = "user", "session123"
    mock_data = {"type": "file", "path": "test.txt"}
    
    await socket_server.create(sid="user123", data=mock_data)
    
    mock_get_conn_info.assert_called_once_with("user123")
    mock_socket_server.emit.assert_called_once_with("create", mock_data, room="session123", skip_sid="user123")
    
@pytest.mark.asyncio
@patch("app.websocket.websocket_server.socket_server", autospec=True)
@patch("app.websocket.websocket_server.get_connection_information", autospec=True)
async def test_rename(mock_get_conn_info, mock_socket_server):
    """
    Test rename event.
    """
    mock_get_conn_info.return_value = "user", "session123"
    mock_data = {"path": "test", "new_path": "new_test"}
    
    await socket_server.rename(sid="user123", data=mock_data)
    
    mock_get_conn_info.assert_called_once_with("user123")
    mock_socket_server.emit.assert_called_once_with("rename", mock_data, room="session123", skip_sid="user123")
    
@pytest.mark.asyncio
@patch("app.websocket.websocket_server.socket_server", autospec=True)
@patch("app.websocket.websocket_server.get_connection_information", autospec=True)
async def test_delete(mock_get_conn_info, mock_socket_server):
    """
    Test delete event.
    """
    mock_get_conn_info.return_value = "user", "session123"
    mock_data = {"path": "test.txt"}
    
    await socket_server.delete(sid="user123", data=mock_data)
    
    mock_get_conn_info.assert_called_once_with("user123")
    mock_socket_server.emit.assert_called_once_with("delete", mock_data, room="session123", skip_sid="user123")
    
@pytest.mark.asyncio
@patch("app.websocket.websocket_server.socket_server", autospec=True)
@patch("app.websocket.websocket_server.get_connection_information", autospec=True)
async def test_environment(mock_get_conn_info, mock_socket_server):
    """
    Test environment event.
    """
    mock_get_conn_info.return_value = "instance", "session123"
    mock_data = {}
    
    await socket_server.environment(sid="instance123", data=mock_data)
    
    mock_get_conn_info.assert_called_once_with("instance123")
    mock_socket_server.emit.assert_called_once_with("environment", mock_data, room="session123", skip_sid="instance123")
    
@pytest.mark.asyncio
@patch("app.websocket.websocket_server.socket_server", autospec=True)
@patch("app.websocket.websocket_server.get_connection_information", autospec=True)
async def test_open_file(mock_get_conn_info, mock_socket_server):
    """
    Test open_file event.
    """
    mock_get_conn_info.return_value = "user", "session123"
    mock_data = {"path": "test.txt"}
    
    await socket_server.open_file(sid="user123", data=mock_data)
    
    mock_get_conn_info.assert_called_once_with("user123")
    mock_socket_server.emit.assert_called_once_with("open_file", mock_data, room="session123", skip_sid="user123")
    
@pytest.mark.asyncio
@patch("app.websocket.websocket_server.socket_server", autospec=True)
@patch("app.websocket.websocket_server.get_connection_information", autospec=True)
async def test_save_file(mock_get_conn_info, mock_socket_server):
    """
    Test save_file event.
    """
    mock_get_conn_info.return_value = "user", "session123"
    mock_data = {"path": "test.txt", "content": "some content"}
    
    await socket_server.save_file(sid="user123", data=mock_data)
    
    mock_get_conn_info.assert_called_once_with("user123")
    mock_socket_server.emit.assert_called_once_with("save_file", mock_data, room="session123", skip_sid="user123")
    
@pytest.mark.asyncio
@patch("app.websocket.websocket_server.socket_server", autospec=True)
@patch("app.websocket.websocket_server.get_connection_information", autospec=True)
async def test_file_content(mock_get_conn_info, mock_socket_server):
    """
    Test file_content event.
    """
    mock_get_conn_info.return_value = "instance", "session123"
    mock_data = {"path": "test.txt", "content": "some content"}
    
    await socket_server.file_content(sid="instance123", data=mock_data)
    
    mock_get_conn_info.assert_called_once_with("instance123")
    mock_socket_server.emit.assert_called_once_with("file_content", mock_data, room="session123", skip_sid="instance123")