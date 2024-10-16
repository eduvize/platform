from unittest.mock import ANY, AsyncMock, Mock, patch
import pytest
from app.websocket.playground.connection_lifecycle import (
    handle_user_connection, 
    handle_instance_connection, 
    handle_user_disconnect, 
    handle_instance_disconnect
)
from app.websocket.playground.cache_keys import (
    get_image_tag_cache_key,
    get_instance_ready_cache_key,
    get_liveness_cache_key,
    get_user_connected_cache_key
)

def create_mock_session(mock_server: Mock) -> AsyncMock:
    # Mock the session method
    mock_session = AsyncMock()
    mock_server.session.return_value = AsyncMock()
    mock_server.session.return_value.__aenter__.return_value = mock_session

    return mock_session

@pytest.mark.asyncio
@patch("app.websocket.playground.connection_lifecycle.get_key", return_value=None)
@patch("app.websocket.playground.connection_lifecycle.set_key", autospec=True)
async def test_handle_user_connection_baseline(
    mock_set_key: Mock,
    mock_get_key: Mock
):
    """
    Tests the handling of newly connect users by validating session variable assignment, environment verification, cache key setting
    and that no events are transmitted when there is no active instance.
    """
    
    # Mock the playground repository
    mock_playground_repo = Mock()
    mock_playground_repo.get_environment.return_value = Mock(image_tag="test_image_tag")
    
    # Mock the server instance
    mock_server = Mock()
    mock_session = create_mock_session(mock_server)
    
    # Cache keys
    image_tag_key = get_image_tag_cache_key("test_environment_id")
    liveness_cache_key = get_liveness_cache_key("test_session_id")
    instance_ready_cache_key = get_instance_ready_cache_key("test_session_id")
    connected_cache_key = get_user_connected_cache_key("test_session_id")
    
    # Call the function
    await handle_user_connection(
        server=mock_server,
        playground_repo=mock_playground_repo,
        sid="test_sid",
        user_id="test_user_id",
        session_id="test_session_id",
        environment_id="test_environment_id"
    )
    
    # Ensure the session method was called once with the correct SID
    mock_server.session.assert_called_once_with("test_sid")
    
    # Assert the session variables were set
    mock_session.__setitem__.assert_any_call("session_id", "test_session_id")
    mock_session.__setitem__.assert_any_call("user_id", "test_user_id")
    mock_session.__setitem__.assert_any_call("environment_id", "test_environment_id")
    
    # Assert the environment was retrieved
    mock_playground_repo.get_environment.assert_called_once_with("test_environment_id")
    
    # Assert the image tag was set
    mock_set_key.assert_any_call(key=image_tag_key, value="test_image_tag")
    
    # Assert the cache keys were retrieved
    mock_get_key.assert_any_call(liveness_cache_key)
    mock_get_key.assert_any_call(instance_ready_cache_key)
    
    # Assert no events were emitted
    mock_server.emit.assert_not_called()
    
    # Assert the user connected cache key was set with an expiration
    mock_set_key.assert_any_call(key=connected_cache_key, value=ANY, expiration=ANY)

@pytest.mark.asyncio
@patch("app.websocket.playground.connection_lifecycle.set_key")
@patch("app.websocket.playground.connection_lifecycle.get_key")
async def test_handle_user_connection_with_live_instance(
    mock_get_key: Mock,
    mock_set_key: Mock,
):
    # Mock the playground repository
    mock_playground_repo = Mock()
    mock_playground_repo.get_environment.return_value = Mock(image_tag="test_image_tag")
    
    # Mock the server instance
    mock_server = Mock()
    mock_server.emit = AsyncMock()
    
    create_mock_session(mock_server)
    
    # Cache keys
    liveness_cache_key = get_liveness_cache_key("test_session_id")
    instance_ready_cache_key = get_instance_ready_cache_key("test_session_id")
    
    # Mock the get_key function to fake an instance being alive but not ready
    def get_key_side_effect(key):
        if key == liveness_cache_key:
            return "1"
        elif key == instance_ready_cache_key:
            return None
        else:
            return None
        
    mock_get_key.side_effect = get_key_side_effect
    
    # Call the function
    await handle_user_connection(
        server=mock_server,
        playground_repo=mock_playground_repo,
        sid="test_sid",
        user_id="test_user_id",
        session_id="test_session_id",
        environment_id="test_environment_id"
    )
    
    # Assert the cache keys were retrieved
    mock_get_key.assert_any_call(liveness_cache_key)
    mock_get_key.assert_any_call(instance_ready_cache_key)
    
    # Assert instance_connected event is sent to the user
    mock_server.emit.assert_any_call("instance_connected", room="test_session_id")
    
    # Assert the user_connected event is sent to the instance
    mock_server.emit.assert_any_call("user_connected", ANY, room="test_session_id")
    
    # Assert that the user DOES NOT get instance_ready event
    assert mock_server.emit.call_count == 2

@pytest.mark.asyncio
@patch("app.websocket.playground.connection_lifecycle.set_key")
@patch("app.websocket.playground.connection_lifecycle.get_key")
async def test_handle_user_connection_with_live_and_ready_instance(
    mock_get_key: Mock,
    mock_set_key: Mock,
):
    # Mock the playground repository
    mock_playground_repo = Mock()
    mock_playground_repo.get_environment.return_value = Mock(image_tag="test_image_tag")
    
    # Mock the server instance
    mock_server = Mock()
    mock_server.emit = AsyncMock()
    
    create_mock_session(mock_server)
    
    # Cache keys
    liveness_cache_key = get_liveness_cache_key("test_session_id")
    instance_ready_cache_key = get_instance_ready_cache_key("test_session_id")
    
    # Mock the get_key function to fake an instance being alive but not ready
    def get_key_side_effect(key):
        if key == liveness_cache_key:
            return "1"
        elif key == instance_ready_cache_key:
            return "1"
        else:
            return None
        
    mock_get_key.side_effect = get_key_side_effect
    
    # Call the function
    await handle_user_connection(
        server=mock_server,
        playground_repo=mock_playground_repo,
        sid="test_sid",
        user_id="test_user_id",
        session_id="test_session_id",
        environment_id="test_environment_id"
    )
    
    # Assert the cache keys were retrieved
    mock_get_key.assert_any_call(liveness_cache_key)
    mock_get_key.assert_any_call(instance_ready_cache_key)
    
    # Assert instance_connected event is sent to the user
    mock_server.emit.assert_any_call("instance_connected", room="test_session_id")
    
    # Assert the user_connected event is sent to the instance
    mock_server.emit.assert_any_call("user_connected", ANY, room="test_session_id")
    
    # Assert that the user gets the instance_ready event
    mock_server.emit.assert_any_call("instance_ready", room="test_session_id")
    
@pytest.mark.asyncio
@patch("app.websocket.playground.connection_lifecycle.get_key", return_value=None)
@patch("app.websocket.playground.connection_lifecycle.set_key")
async def test_handle_instance_connection_baseline(
    mock_set_key: Mock,
    mock_get_key: Mock
):
    # Mock the server instance
    mock_server = Mock()
    mock_server.emit = AsyncMock()
    mock_session = create_mock_session(mock_server)
    
    # Cache keys
    user_connected_key = get_user_connected_cache_key("test_session_id")
    image_tag_key = get_image_tag_cache_key("test_environment_id")
    
    # Call the function
    await handle_instance_connection(
        server=mock_server,
        sid="test_sid",
        session_id="test_session_id",
        environment_id="test_environment_id",
        instance_hostname="test_instance_hostname"
    )
    
    # Assert the session variables were set
    mock_session.__setitem__.assert_any_call("session_id", "test_session_id")
    mock_session.__setitem__.assert_any_call("instance_hostname", "test_instance_hostname")
    
    # Assert the cache keys were retrieved
    mock_get_key.assert_any_call(user_connected_key)
    mock_get_key.assert_any_call(image_tag_key)
    
    # Assert the instance_connected event was sent
    mock_server.emit.assert_any_call("instance_connected", room="test_session_id")
    
    # Assert no other events were sent
    assert mock_server.emit.call_count == 1
    
    # Assert the liveness cache key was set
    mock_set_key.assert_any_call(key=get_liveness_cache_key("test_session_id"), value=ANY)

@pytest.mark.asyncio
@patch("app.websocket.playground.connection_lifecycle.get_key")
@patch("app.websocket.playground.connection_lifecycle.set_key")
async def test_handle_instance_connection_with_active_user(
    mock_set_key: Mock,
    mock_get_key: Mock
):
    # Mock the server instance
    mock_server = Mock()
    mock_server.emit = AsyncMock()
    mock_session = create_mock_session(mock_server)
    
    # Cache keys
    user_connected_key = get_user_connected_cache_key("test_session_id")
    image_tag_key = get_image_tag_cache_key("test_environment_id")
    
    # Set up get_key side effect
    def get_key_side_effect(key):
        if key == user_connected_key:
            return "1"
        elif key == image_tag_key:
            return "test_image_tag"
        else:
            return None
        
    mock_get_key.side_effect = get_key_side_effect
    
    # Call the function
    await handle_instance_connection(
        server=mock_server,
        sid="test_sid",
        session_id="test_session_id",
        environment_id="test_environment_id",
        instance_hostname="test_instance_hostname"
    )
    
    # Assert the cache keys were retrieved
    mock_get_key.assert_any_call(user_connected_key)
    mock_get_key.assert_any_call(image_tag_key)
    
    # Assert the instance_connected event was sent
    mock_server.emit.assert_any_call("instance_connected", room="test_session_id")
    
    # Assert that the user_connected event was sent to the instance
    mock_server.emit.assert_any_call("user_connected", ANY, room="test_session_id")
    
    # Assert no other events were sent
    assert mock_server.emit.call_count == 2
    
    # Assert the liveness cache key was set
    mock_set_key.assert_any_call(key=get_liveness_cache_key("test_session_id"), value=ANY)

@pytest.mark.asyncio
@patch("app.websocket.playground.connection_lifecycle.delete_key")
async def test_handle_user_disconnect(
    mock_delete_key: Mock,
):
    # Mock the server
    mock_server = Mock()
    mock_server.emit = AsyncMock()
    
    # Cache keys
    user_connected_key = get_user_connected_cache_key("test_session_id")
    image_tag_key = get_image_tag_cache_key("test_environment_id")
    
    # Call the function
    await handle_user_disconnect(
        server=mock_server,
        sid="test_sid",
        session_id="test_session_id",
        environment_id="test_environment_id"
    )
    
    # Assert user_disconnect event is sent to the instance, skipping the user's SID
    mock_server.emit.assert_any_call("user_disconnected", room="test_session_id", skip_sid="test_sid")
    
    # Assert cache keys were deleted
    mock_delete_key.assert_any_call(user_connected_key)
    mock_delete_key.assert_any_call(image_tag_key)

@pytest.mark.asyncio
@patch("app.websocket.playground.connection_lifecycle.delete_key")
async def test_handle_instance_disconnect(
    mock_delete_key: Mock,
):
    # Mock the server
    mock_server = Mock()
    mock_server.emit = AsyncMock()
    
    # Cache keys
    liveness_cache_key = get_liveness_cache_key("test_session_id")
    instance_ready_cache_key = get_instance_ready_cache_key("test_session_id")
    
    # Call the function
    await handle_instance_disconnect(
        server=mock_server,
        sid="test_sid",
        session_id="test_session_id"
    )
    
    # Assert instance_disconnected event is sent to the user, skipping the instance's SID
    mock_server.emit.assert_any_call("instance_disconnected", room="test_session_id", skip_sid="test_sid")
    
    # Assert cache keys were deleted
    mock_delete_key.assert_any_call(liveness_cache_key)
    mock_delete_key.assert_any_call(instance_ready_cache_key)