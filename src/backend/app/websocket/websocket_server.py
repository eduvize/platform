import logging
from typing import Optional
from socketio import AsyncServer
from app.utilities.jwt import decode_token, InvalidJWTToken
from common.cache import set_key, get_key, delete_key
from config import get_playground_token_secret

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

socket_server = AsyncServer(async_mode="asgi", cors_allowed_origins="*")

@socket_server.event
async def connect(sid: str, environment_data: dict, extra: Optional[dict] = None):
    token = get_token(environment_data)
    
    if token is None:
        logger.info(f"Connection from {sid} failed due to missing token")
        return False
    
    try:
        decoded = decode_token(token=token, secret=get_playground_token_secret())
        session_id = decoded.get("session_id", None)
        instance_hostname = decoded.get("hostname", None)
        user_id = decoded.get("user_id", None)
        
        if session_id is None:
            logger.info(f"Connection from {sid} failed due to missing session ID")
            return False
        
        # Add the socket connection to the session room
        await socket_server.enter_room(sid, session_id)
        
        # If it's a user
        if user_id is not None:
            logger.info(f"Connection from {sid} succeeded with user ID {user_id}, session ID {session_id}")
            async with socket_server.session(sid) as session:
                session["session_id"] = session_id
                session["user_id"] = user_id
                
            is_alive = get_key(get_liveness_cache_key(session_id))
            
            if is_alive is not None:
                await socket_server.emit("instance_connected", room=session_id) # Notify the user of the instance connection
                await socket_server.emit("user_connected", room=session_id) # Notify the instance of the user connection
                
            connected_key = get_user_connected_cache_key(session_id)
            
            set_key(
                key=connected_key,
                value="1",
                expiration=5 * 60 # 5 minutes
            )
                
        # If it's an instance
        if instance_hostname is not None:
            logger.info(f"Connection from {sid} succeeded with hostname {instance_hostname}, session ID {session_id}")
            async with socket_server.session(sid) as session:
                session["session_id"] = session_id
                session["instance_hostname"] = instance_hostname
                
            user_connected_key = get_user_connected_cache_key(session_id)
            
            if get_key(user_connected_key) is not None:
                await socket_server.emit("user_connected", room=session_id) # Notify the instance of the user connection
                
            set_key(
                key=get_liveness_cache_key(session_id),
                value="1",
                expiration=5 * 60 # 5 minutes
            )
            
            await socket_server.emit("instance_connected", room=session_id) # Notify the user of the instance connection
        
    except InvalidJWTToken:
        logger.info(f"Connection from {sid} failed due to invalid token")
        logger.info(f"Token: {token}")
        return False
    
    return True

@socket_server.event
async def disconnect(sid: str):
    async with socket_server.session(sid) as session:
        session_id = session.get("session_id", None)
        user_id = session.get("user_id", None)
        instance_hostname = session.get("instance_hostname", None)
        
        if user_id is not None:
            logger.info(f"User {user_id} disconnected")
            await socket_server.emit("user_disconnected", room=session_id) # Notify the instance
            
            # delete the user connected key
            delete_key(get_user_connected_cache_key(session_id))
        
        if instance_hostname is not None and session_id is not None:
            logger.info(f"Instance {instance_hostname} disconnected")
            await socket_server.emit("instance_disconnected", room=session_id) # Notify the user
            
            # delete the liveness key
            delete_key(get_liveness_cache_key(session_id))

@socket_server.event
async def terminal_input(sid: str, t_input: str):
    async with socket_server.session(sid) as session:
        session_id = session.get("session_id", None)
        
        if session_id is None:
            return

        await socket_server.emit("terminal_input", t_input, room=session_id)
        
@socket_server.event
async def terminal_output(sid: str, output: str):
    async with socket_server.session(sid) as session:
        session_id = session.get("session_id", None)
        
        if session_id is None:
            return

        await socket_server.emit("terminal_output", output, room=session_id)
        
@socket_server.event
async def terminal_resize(sid: str, data: dict):
    async with socket_server.session(sid) as session:
        session_id = session.get("session_id", None)
        
        if session_id is None:
            return
        
        logger.info(f"Resizing terminal for session {session_id} to {data['rows']}x{data['columns']}")
        
        await socket_server.emit("terminal_resize", data, room=session_id)
        
@socket_server.event
async def create(sid: str, data: dict):
    async with socket_server.session(sid) as session:
        session_id = session.get("session_id", None)
        
        if session_id is None:
            return
        
        logger.info(f"Creating new filesystem entry in session {session_id}: {data['type']}, {data['path']}")
        
        await socket_server.emit("create", data, room=session_id)
        
@socket_server.event
async def rename(sid: str, data: dict):
    async with socket_server.session(sid) as session:
        session_id = session.get("session_id", None)
        
        if session_id is None:
            return
        
        logger.info(f"Renaming filesystem entry in session {session_id}: {data['path']}, {data['new_path']}")
        
        await socket_server.emit("rename", data, room=session_id)
        
@socket_server.event
async def delete(sid: str, data: dict):
    async with socket_server.session(sid) as session:
        session_id = session.get("session_id", None)
        
        if session_id is None:
            return
        
        logger.info(f"Deleting filesystem entry in session {session_id}: {data['path']}")
        
        await socket_server.emit("delete", data, room=session_id)
        
@socket_server.event
async def environment(sid: str, data: dict):
    async with socket_server.session(sid) as session:
        session_id = session.get("session_id", None)
        instance_hostname = session.get("instance_hostname", None)
        
        if session_id is None:
            return
        
        if instance_hostname is None:
            return # This event is only for instances
        
        logger.info(f"Updating environment for session {session_id} on instance {instance_hostname}")
        
        await socket_server.emit("environment", data, room=session_id)
        
@socket_server.event
async def open_file(sid: str, data: dict):
    async with socket_server.session(sid) as session:
        session_id = session.get("session_id", None)
        
        if session_id is None:
            return
        
        path = data.get("path", None)
        
        logger.info(f"Opening file {path} in session {session_id}")
        
        await socket_server.emit("open_file", data, room=session_id)
    
@socket_server.event
async def save_file(sid: str, data: dict):
    async with socket_server.session(sid) as session:
        session_id = session.get("session_id", None)
        
        if session_id is None:
            return
        
        path = data.get("path", None)
        
        logger.info(f"Saving file {path} in session {session_id}")
        
        await socket_server.emit("save_file", data, room=session_id)
        
@socket_server.event
async def file_content(sid: str, data: dict):
    async with socket_server.session(sid) as session:
        session_id = session.get("session_id", None)
        
        if session_id is None:
            return
        
        path = data.get("path", None)
        
        logger.info(f"Sending file content to user for {path} in session {session_id}")
        
        await socket_server.emit("file_content", data, room=session_id)
    
def get_liveness_cache_key(session_id: str) -> str:
    """
    Generates a cache key for the liveness status of a session instance.

    Args:
        session_id (str): The ID of the session to generate the key for.

    Returns:
        str: The cache key.
    """
    return f"playground_session:{session_id}:alive"

def get_user_connected_cache_key(session_id: str) -> str:
    """
    Generates a cache key for the user connected status of a session instance.

    Args:
        session_id (str): The ID of the session to generate the key for.

    Returns:
        str: The cache key.
    """
    return f"playground_session:{session_id}:user_connected"

def get_token(environ: dict) -> Optional[str]:
    """
    Extracts the token from the header information associated with the connect event.

    Args:
        environ (dict): The environment data from the websocket connection.

    Returns:
        Optional[str]: The token if it exists, as a UTF-8 string.
    """
    scope = environ.get("asgi.scope")
    
    if not scope:
        return None
    
    headers = scope.get("headers")
    
    if not headers:
        return None
    
    for header in headers:
        key, value = header
        if key.decode("utf-8").lower() == "authorization":
            try:
                token = value.decode("utf-8")
                if token.startswith("Bearer "):
                    return token[len("Bearer "):].strip()
                else:
                    logger.warning(f"Authorization header does not start with 'Bearer ': {token}")
                    return None
            except UnicodeDecodeError as e:
                logger.error(f"Failed to decode token: {e}")
                return None
    
    return None