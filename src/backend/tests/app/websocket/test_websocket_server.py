import pytest
from unittest.mock import ANY, AsyncMock, MagicMock, Mock, patch
from app.websocket.websocket_server import InvalidJWTToken
import app.websocket.websocket_server as socket_server

@pytest.mark.asyncio
@patch("app.websocket.websocket_server.socket_server", autospec=True)
@patch("app.websocket.websocket_server.decode_token")
@patch("app.websocket.websocket_server.get_key", return_value=None)
@patch("app.websocket.websocket_server.set_key", autospec=True)
@patch("app.websocket.websocket_server.PlaygroundRepository", autospec=True)
async def test_connect_user_success_without_active_instance(
    mock_playground_repo_inst: Mock, 
    mock_set_key: Mock, 
    mock_get_key: Mock, 
    mock_decode_token: Mock, 
    mock_socket_server: Mock
):
    """
    Verify that user token validation works correctly, that they are put in the session room, and connected/image tag keys are set.
    In this scenario, the user is the first to connect, meaning the server should not attempt to notify the instance.
    """
    # Mock the decoded token
    mock_decode_token.return_value = {
        "session_id": "session123",
        "environment_id": "environment_id",
        "user_id": "user456",
    }
    
    # No related keys should be set at this point since the user is first to connect
    mock_get_key.return_value = None
    
    # Mock successful connection to the socket server
    mock_socket_server.connect = AsyncMock(return_value=True)
    
    # Mock successful environment retrieval
    mock_playground_repo_inst.return_value = Mock()
    mock_playground_repo_inst.return_value.get_environment = Mock(return_value=Mock(id="environment_id", image_tag="tag"))

    environment_data = {
        "asgi.scope": {
            "headers": [(b'authorization', b'Bearer valid.token.here')]
        }
    }

    result = await socket_server.connect(sid="user123", environment_data=environment_data)

    assert result is True
    mock_socket_server.enter_room.assert_called_once_with("user123", "session123")
    mock_set_key.assert_any_call(key=socket_server.get_user_connected_cache_key("session123"), value=ANY, expiration=5*60)
    mock_set_key.assert_any_call(key=socket_server.get_image_tag_cache_key("environment_id"), value="tag")
    mock_socket_server.emit.assert_not_called()
    
@pytest.mark.asyncio
@patch("app.websocket.websocket_server.socket_server", autospec=True)
@patch("app.websocket.websocket_server.decode_token")
@patch("app.websocket.websocket_server.get_key", return_value=None)
@patch("app.websocket.websocket_server.set_key", autospec=True)
@patch("app.websocket.websocket_server.PlaygroundRepository", autospec=True)
async def test_connect_user_success_with_active_instance(
    mock_playground_repo_inst: Mock, 
    mock_set_key: Mock, 
    mock_get_key: Mock, 
    mock_decode_token: Mock, 
    mock_socket_server: Mock
):
    """
    Test that a user connecting after an instance has already connected appropriately notifies both parties of each other's presence and sets
    the necessary keys.
    """
    
    # Mock the decoded token
    mock_decode_token.return_value = {
        "session_id": "session123",
        "environment_id": "environment_id",
        "user_id": "user456",
    }
    
    liveness_key = socket_server.get_liveness_cache_key("session123")
    
    def key_return_side_effect(key):
        if key == liveness_key:
            return "1"
        return True
    
    mock_get_key.side_effect = key_return_side_effect
    mock_socket_server.connect = AsyncMock(return_value=True)
    mock_playground_repo_inst.return_value = Mock()
    mock_playground_repo_inst.return_value.get_environment = Mock(return_value=Mock(id="environment_id", image_tag="tag"))

    environment_data = {
        "asgi.scope": {
            "headers": [(b'authorization', b'Bearer valid.token.here')]
        }
    }

    result = await socket_server.connect(sid="user123", environment_data=environment_data)

    assert result is True
    mock_socket_server.enter_room.assert_called_once_with("user123", "session123")
    mock_set_key.assert_any_call(key=socket_server.get_user_connected_cache_key("session123"), value=ANY, expiration=5*60)
    mock_set_key.assert_any_call(key=socket_server.get_image_tag_cache_key("environment_id"), value="tag")
    mock_socket_server.emit.assert_any_call("user_connected", ANY, room="session123")
    mock_socket_server.emit.assert_any_call("instance_connected", room="session123")

@pytest.mark.asyncio
@patch("app.websocket.websocket_server.socket_server", autospec=True)
@patch("app.websocket.websocket_server.decode_token", side_effect=InvalidJWTToken)
async def test_connect_invalid_token(
    mock_decode_token: Mock,
    mock_socket_server: Mock
):
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
async def test_connect_missing_session_id(
    mock_decode_token: Mock, 
    mock_get_key: Mock, 
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
@patch("app.websocket.websocket_server.delete_key", autospec=True)
@patch("app.websocket.websocket_server.get_connection_information", autospec=True)
async def test_disconnect_user(
    mock_get_conn_info: Mock, 
    mock_delete_key: Mock, 
    mock_socket_server: Mock
):
    """
    Tests that users disconnecting triggers the user_disconnected event to the session room
    and removes related keys.
    """
    mock_get_conn_info.return_value = "user", "session123", "environment_id"
    cache_key = socket_server.get_user_connected_cache_key("session123")
    image_key = socket_server.get_image_tag_cache_key("environment_id")
    
    await socket_server.disconnect(sid="user123")
    
    mock_get_conn_info.assert_called_once_with("user123")
    mock_socket_server.emit.assert_called_once_with("user_disconnected", room="session123", skip_sid="user123")
    mock_delete_key.assert_any_call(cache_key)
    mock_delete_key.assert_any_call(image_key)
    
@pytest.mark.asyncio
@patch("app.websocket.websocket_server.socket_server", autospec=True)
@patch("app.websocket.websocket_server.delete_key", autospec=True)
@patch("app.websocket.websocket_server.get_connection_information", autospec=True)
async def test_disconnect_instance(
    mock_get_conn_info: Mock, 
    mock_delete_key: Mock, 
    mock_socket_server: Mock
):
    """
    Test that instances disconnecting triggers the instance_disconnected event to the session room
    and removes related keys.
    """
    mock_get_conn_info.return_value = "instance", "session123", "environment_id"
    liveness_key = socket_server.get_liveness_cache_key("session123")
    ready_key = socket_server.get_instance_ready_cache_key("session123")
    
    await socket_server.disconnect(sid="inst123")
    
    mock_get_conn_info.assert_called_once_with("inst123")
    mock_socket_server.emit.assert_called_once_with("instance_disconnected", room="session123", skip_sid="inst123")
    mock_delete_key.assert_any_call(liveness_key)
    mock_delete_key.assert_any_call(ready_key)

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