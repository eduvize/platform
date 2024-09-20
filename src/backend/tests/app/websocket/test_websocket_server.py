import pytest
from unittest.mock import ANY, AsyncMock, MagicMock, Mock, patch
from app.websocket.websocket_server import InvalidJWTToken
import app.websocket.websocket_server as socket_server

@pytest.mark.asyncio
@patch("app.websocket.websocket_server.socket_server", autospec=True)
@patch("app.websocket.websocket_server.decode_token", autospec=True)
@patch("app.websocket.websocket_server.handle_user_connection", autospec=True)
@patch("app.websocket.websocket_server.handle_instance_connection", autospec=True)
@patch("app.websocket.websocket_server.get_playground_token_secret", autospec=True)
async def test_connect_user_success_without_active_instance(
    mock_get_playground_token_secret: Mock,
    mock_handle_instance_connection: Mock,
    mock_handle_user_connection: Mock,
    mock_decode_token: Mock, 
    mock_socket_server: Mock
):
    """
    Verify that user token validation works correctly, that they are put in the session room, and connected/image tag keys are set.
    In this scenario, the user is the first to connect, meaning the server should not attempt to notify the instance.
    """
    # Mock signing key
    mock_get_playground_token_secret.return_value = "secret key"
    
    # Mock the decoded token
    mock_decode_token.return_value = {
        "session_id": "session123",
        "environment_id": "environment_id",
        "user_id": "user456",
    }
        
    # Mock connect result and environment data
    mock_socket_server.connect = AsyncMock(return_value=True)
    environment_data = {
        "asgi.scope": {
            "headers": [(b'authorization', b'Bearer valid.token.here')]
        }
    }

    await socket_server.connect(sid="user123", environment_data=environment_data)

    mock_decode_token.assert_any_call(token="valid.token.here", secret="secret key")
    mock_handle_user_connection.assert_called_once()
    mock_handle_instance_connection.assert_not_called()

@pytest.mark.asyncio
@patch("app.websocket.websocket_server.handle_user_connection", autospec=True)
@patch("app.websocket.websocket_server.handle_instance_connection", autospec=True)
@patch("app.websocket.websocket_server.decode_token", side_effect=InvalidJWTToken)
async def test_connect_invalid_token(
    mock_decode_token: Mock,
    mock_handle_instance_connection: Mock,
    mock_handle_user_connection: Mock
):
    """
    Test connection failure due to an invalid JWT token.
    """
    environment_data = {
        "asgi.scope": {
            "headers": [(b'authorization', b'Bearer invalid.token.here')]
        }
    }
    
    await socket_server.connect(sid="user123", environment_data=environment_data)
    
    mock_decode_token.assert_called_once_with(token="invalid.token.here", secret=ANY)
    mock_handle_user_connection.assert_not_called()
    mock_handle_instance_connection.assert_not_called()

@pytest.mark.asyncio
@patch("app.websocket.websocket_server.socket_server", autospec=True)
@patch("app.websocket.websocket_server.decode_token")
async def test_connect_missing_session_id(
    mock_decode_token: Mock, 
    mock_socket_server: Mock
):
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
@patch("app.websocket.websocket_server.handle_user_disconnect", autospec=True)
@patch("app.websocket.websocket_server.get_connection_information", autospec=True)
async def test_disconnect_user(
    mock_get_conn_info: Mock, 
    mock_handle_user_disconnect: Mock,
    mock_socket_server: Mock
):
    """
    Tests that users disconnecting triggers the user_disconnected event to the session room
    and removes related keys.
    """
    mock_get_conn_info.return_value = "user", "session123", "environment_id"
    
    await socket_server.disconnect(sid="user123")
    
    mock_handle_user_disconnect.assert_called_once_with(
        server=mock_socket_server,
        sid="user123",
        session_id="session123",
        environment_id="environment_id"
    )

@pytest.mark.asyncio
@patch("app.websocket.websocket_server.socket_server", autospec=True)
@patch("app.websocket.websocket_server.get_connection_information", autospec=True)
async def test_terminal_input(
    mock_get_conn_info: Mock, 
    mock_socket_server: Mock
):
    """
    Test terminal input event.
    """
    mock_get_conn_info.return_value = "user", "session123", "environment_id"
    
    await socket_server.terminal_input(sid="user123", t_input="some command")

    mock_get_conn_info.assert_called_once_with("user123")
    mock_socket_server.emit.assert_called_once_with("terminal_input", "some command", room="session123", skip_sid="user123")

@pytest.mark.asyncio
@patch("app.websocket.websocket_server.socket_server", autospec=True)
@patch("app.websocket.websocket_server.get_connection_information", autospec=True)
async def test_terminal_output(
    mock_get_conn_info: Mock, 
    mock_socket_server: Mock
):
    """
    Test terminal output event.
    """
    mock_get_conn_info.return_value = "instance", "session123", "environment_id"
    
    await socket_server.terminal_output(sid="instance123", output="output text")

    mock_get_conn_info.assert_called_once_with("instance123")
    mock_socket_server.emit.assert_called_once_with("terminal_output", "output text", room="session123", skip_sid="instance123")

@pytest.mark.asyncio
@patch("app.websocket.websocket_server.socket_server", autospec=True)
@patch("app.websocket.websocket_server.get_connection_information", autospec=True)
async def test_terminal_resize(
    mock_get_conn_info: Mock, 
    mock_socket_server: Mock
):
    """
    Test terminal resize event.
    """
    mock_get_conn_info.return_value = "user", "session123", "environment_id"
    
    data = {"rows": 24, "columns": 80}
    await socket_server.terminal_resize(sid="user123", data=data)

    mock_get_conn_info.assert_called_once_with("user123")
    mock_socket_server.emit.assert_called_once_with("terminal_resize", data, room="session123", skip_sid="user123")

@pytest.mark.asyncio
@patch("app.websocket.websocket_server.socket_server", autospec=True)
@patch("app.websocket.websocket_server.get_connection_information", autospec=True)
async def test_create(
    mock_get_conn_info: Mock, 
    mock_socket_server: Mock
):
    """
    Test create event.
    """
    mock_get_conn_info.return_value = "user", "session123", "environment_id"
    mock_data = {"type": "file", "path": "test.txt"}
    
    await socket_server.create(sid="user123", data=mock_data)
    
    mock_get_conn_info.assert_called_once_with("user123")
    mock_socket_server.emit.assert_called_once_with("create", mock_data, room="session123", skip_sid="user123")
    
@pytest.mark.asyncio
@patch("app.websocket.websocket_server.socket_server", autospec=True)
@patch("app.websocket.websocket_server.get_connection_information", autospec=True)
async def test_rename(
    mock_get_conn_info: Mock, 
    mock_socket_server: Mock
):
    """
    Test rename event.
    """
    mock_get_conn_info.return_value = "user", "session123", "environment_id"
    mock_data = {"path": "test", "new_path": "new_test"}
    
    await socket_server.rename(sid="user123", data=mock_data)
    
    mock_get_conn_info.assert_called_once_with("user123")
    mock_socket_server.emit.assert_called_once_with("rename", mock_data, room="session123", skip_sid="user123")
    
@pytest.mark.asyncio
@patch("app.websocket.websocket_server.socket_server", autospec=True)
@patch("app.websocket.websocket_server.get_connection_information", autospec=True)
async def test_delete(
    mock_get_conn_info: Mock, 
    mock_socket_server: Mock
):
    """
    Test delete event.
    """
    mock_get_conn_info.return_value = "user", "session123", "environment_id"
    mock_data = {"path": "test.txt"}
    
    await socket_server.delete(sid="user123", data=mock_data)
    
    mock_get_conn_info.assert_called_once_with("user123")
    mock_socket_server.emit.assert_called_once_with("delete", mock_data, room="session123", skip_sid="user123")
    
@pytest.mark.asyncio
@patch("app.websocket.websocket_server.socket_server", autospec=True)
@patch("app.websocket.websocket_server.get_connection_information", autospec=True)
async def test_environment(
    mock_get_conn_info: Mock, 
    mock_socket_server: Mock
):
    """
    Test environment event.
    """
    mock_get_conn_info.return_value = "instance", "session123", "environment_id"
    mock_data = {}
    
    await socket_server.environment(sid="instance123", data=mock_data)
    
    mock_get_conn_info.assert_called_once_with("instance123")
    mock_socket_server.emit.assert_called_once_with("environment", mock_data, room="session123", skip_sid="instance123")
    
@pytest.mark.asyncio
@patch("app.websocket.websocket_server.socket_server", autospec=True)
@patch("app.websocket.websocket_server.get_connection_information", autospec=True)
async def test_open_file(
    mock_get_conn_info: Mock, 
    mock_socket_server: Mock
):
    """
    Test open_file event.
    """
    mock_get_conn_info.return_value = "user", "session123", "environment_id"
    mock_data = {"path": "test.txt"}
    
    await socket_server.open_file(sid="user123", data=mock_data)
    
    mock_get_conn_info.assert_called_once_with("user123")
    mock_socket_server.emit.assert_called_once_with("open_file", mock_data, room="session123", skip_sid="user123")
    
@pytest.mark.asyncio
@patch("app.websocket.websocket_server.socket_server", autospec=True)
@patch("app.websocket.websocket_server.get_connection_information", autospec=True)
async def test_save_file(
    mock_get_conn_info: Mock, 
    mock_socket_server: Mock
):
    """
    Test save_file event.
    """
    mock_get_conn_info.return_value = "user", "session123", "environment_id"
    mock_data = {"path": "test.txt", "content": "some content"}
    
    await socket_server.save_file(sid="user123", data=mock_data)
    
    mock_get_conn_info.assert_called_once_with("user123")
    mock_socket_server.emit.assert_called_once_with("save_file", mock_data, room="session123", skip_sid="user123")
    
@pytest.mark.asyncio
@patch("app.websocket.websocket_server.socket_server", autospec=True)
@patch("app.websocket.websocket_server.get_connection_information", autospec=True)
async def test_file_content(
    mock_get_conn_info: Mock, 
    mock_socket_server: Mock
):
    """
    Test file_content event.
    """
    mock_get_conn_info.return_value = "instance", "session123", "environment_id"
    mock_data = {"path": "test.txt", "content": "some content"}
    
    await socket_server.file_content(sid="instance123", data=mock_data)
    
    mock_get_conn_info.assert_called_once_with("instance123")
    mock_socket_server.emit.assert_called_once_with("file_content", mock_data, room="session123", skip_sid="instance123")