import logging
from typing import Literal, Optional, Tuple
from socketio import AsyncServer
from app.repositories import PlaygroundRepository
from app.utilities.jwt import decode_token, InvalidJWTToken
from common.cache import set_key
from config import get_playground_token_secret
from .connection_lifecycle import handle_instance_connection, handle_user_connection, handle_instance_disconnect, handle_user_disconnect
from .cache_keys import get_instance_ready_cache_key

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

socket_server = AsyncServer(async_mode="asgi", cors_allowed_origins="*", async_handlers=True)

@socket_server.event
async def connect(
    sid: str, 
    environment_data: dict, 
    extra: Optional[dict] = None
):
    token = get_token(environment_data)
    
    if token is None:
        logger.info(f"Connection from {sid} failed due to missing token")
        return False
    
    try:
        decoded = decode_token(token=token, secret=get_playground_token_secret())
        session_id = decoded.get("session_id", None)
        environment_id = decoded.get("environment_id", None)
        instance_hostname = decoded.get("hostname", None)
        user_id = decoded.get("user_id", None)
        
        if session_id is None:
            logger.info(f"Connection from {sid} failed due to missing session ID")
            return False
        
        # Add the socket connection to the session room
        await socket_server.enter_room(sid, session_id)
        
        # If it's a user
        if user_id is not None:
            playground_repo = PlaygroundRepository()
            await handle_user_connection(
                server=socket_server, 
                playground_repo=playground_repo, 
                sid=sid, 
                user_id=user_id, 
                session_id=session_id, 
                environment_id=environment_id
            )
                
        # If it's an instance
        if instance_hostname is not None:
            await handle_instance_connection(
                server=socket_server,
                sid=sid, 
                session_id=session_id, 
                environment_id=environment_id, 
                instance_hostname=instance_hostname
            )
        
    except InvalidJWTToken:
        logger.info(f"Connection from {sid} failed due to invalid token")
        logger.info(f"Token: {token}")
        return False
    
    return True

@socket_server.event
async def setup_status(sid: str, status: str):
    client_type, session_id, environment_id = await get_connection_information(sid)
    
    if client_type == "instance" and session_id:
        logger.info(f"Received setup status from {client_type} {session_id}: {status}")
        
        await socket_server.emit("setup_status", status, room=session_id, skip_sid=sid)

@socket_server.event
async def ready(sid: str):
    client_type, session_id, env_id = await get_connection_information(sid)
    
    if client_type == "instance" and session_id:
        logger.info(f"Instance {session_id} is ready")
        
        set_key(
            key=get_instance_ready_cache_key(session_id),
            value="1",
        )
        await socket_server.emit("instance_ready", room=session_id, skip_sid=sid)

@socket_server.event
async def disconnect(sid: str):
    client_type, session_id, environment_id = await get_connection_information(sid)
    
    if client_type and session_id:
        if client_type == "instance":
            await handle_instance_disconnect(
                server=socket_server,
                sid=sid,
                session_id=session_id,
            )
            
        if client_type == "user":
            await handle_user_disconnect(
                server=socket_server,
                sid=sid,
                session_id=session_id,
                environment_id=environment_id
            )

@socket_server.event
async def terminal_input(sid: str, t_input: str):
    client_type, session_id, env_id = await get_connection_information(sid)
    
    if client_type == "user" and session_id:
        logger.info(f"Received terminal input from {client_type} {session_id}: {t_input}")
        
        await socket_server.emit("terminal_input", t_input, room=session_id, skip_sid=sid)
    
@socket_server.event
async def terminal_output(sid: str, output: str):
    client_type, session_id, env_id = await get_connection_information(sid)
    
    if client_type == "instance" and session_id:
        logger.info(f"Sending terminal output to {client_type} {session_id}: {output}")
        
        await socket_server.emit("terminal_output", output, room=session_id, skip_sid=sid)
    
@socket_server.event
async def terminal_resize(sid: str, data: dict):
    client_type, session_id, env_id = await get_connection_information(sid)
    
    if client_type == "user" and session_id:
        logger.info(f"Resizing terminal for {client_type} {session_id} to {data['rows']}x{data['columns']}")
        
        await socket_server.emit("terminal_resize", data, room=session_id, skip_sid=sid)
    
@socket_server.event
async def create(sid: str, data: dict):
    client_type, session_id, env_id = await get_connection_information(sid)
    
    if client_type == "user" and session_id:
        logger.info(f"Creating new filesystem entry for {client_type} {session_id}: {data['type']}, {data['path']}")
        
        await socket_server.emit("create", data, room=session_id, skip_sid=sid)
    
@socket_server.event
async def rename(sid: str, data: dict):
    client_type, session_id, env_id = await get_connection_information(sid)
    
    if client_type == "user" and session_id:
        logger.info(f"Renaming filesystem entry for {client_type} {session_id}: {data['path']}, {data['new_path']}")
        
        await socket_server.emit("rename", data, room=session_id, skip_sid=sid)
        
@socket_server.event
async def delete(sid: str, data: dict):
    client_type, session_id, env_id = await get_connection_information(sid)
    
    if client_type == "user" and session_id:
        logger.info(f"Deleting filesystem entry for {client_type} {session_id}: {data['path']}")
        
        await socket_server.emit("delete", data, room=session_id, skip_sid=sid)
        
@socket_server.event
async def environment(sid: str, data: dict):
    client_type, session_id, env_id = await get_connection_information(sid)
    
    if client_type == "instance" and session_id:
        logger.info(f"Updating environment for {client_type} {session_id}")
        
        await socket_server.emit("environment", data, room=session_id, skip_sid=sid)
        
@socket_server.event
async def open_file(sid: str, data: dict):
    client_type, session_id, env_id = await get_connection_information(sid)
    
    if client_type == "user" and session_id:
        logger.info(f"Opening file {data['path']} for {client_type} {session_id}")
        
        await socket_server.emit("open_file", data, room=session_id, skip_sid=sid)
    
@socket_server.event
async def save_file(sid: str, data: dict):
    client_type, session_id, env_id = await get_connection_information(sid)
    
    if client_type == "user" and session_id:
        logger.info(f"Saving file {data['path']} for {client_type} {session_id}")
        
        await socket_server.emit("save_file", data, room=session_id, skip_sid=sid)
    
@socket_server.event
async def file_content(sid: str, data: dict):
    client_type, session_id, env_id = await get_connection_information(sid)
    
    if client_type == "instance" and session_id:
        logger.info(f"Sending file content to user for {data['path']} in session {session_id}")
        
        await socket_server.emit("file_content", data, room=session_id, skip_sid=sid)

@socket_server.event
async def subscribe_to_path(sid: str, data: dict):
    client_type, session_id, env_id = await get_connection_information(sid)
    
    if client_type == "user" and session_id:
        logger.info(f"Subscribing to path {data['path']} in session {session_id}")
        
        await socket_server.emit("subscribe_to_path", data, room=session_id, skip_sid=sid)
        
@socket_server.event
async def unsubscribe_from_path(sid: str, data: dict):
    client_type, session_id, env_id = await get_connection_information(sid)
    
    if client_type == "user" and session_id:
        logger.info(f"Unsubscribing from path {data['path']} in session {session_id}")
        
        await socket_server.emit("unsubscribe_from_path", data, room=session_id, skip_sid=sid)

@socket_server.event
async def get_directory(sid: str, data: dict):
    client_type, session_id, env_id = await get_connection_information(sid)
    
    if client_type == "user" and session_id:
        logger.info(f"Getting directory for {data['path']} in session {session_id}")
        
        await socket_server.emit("get_directory", data, room=session_id, skip_sid=sid)
        
@socket_server.event
async def directory_contents(sid: str, data: dict):
    client_type, session_id, env_id = await get_connection_information(sid)
    
    if client_type == "instance" and session_id:
        logger.info(f"Sending directory contents to user for {data['path']} in session {session_id}")
        
        await socket_server.emit("directory_contents", data, room=session_id, skip_sid=sid)
        
async def get_connection_information(sid: str) -> Tuple[Literal["user", "instance", None], Optional[str], Optional[str]]:
    """
    Gets the client type and session ID associated with a socket connection.

    Returns:
        Tuple[Literal["user", "instance", None], str]: The client type and session ID.
    """
    async with socket_server.session(sid) as session:
        session_id = session.get("session_id", None)
        user_id = session.get("user_id", None)
        instance_hostname = session.get("instance_hostname", None)
        environment_id = session.get("environment_id", None)
        
        if user_id is not None:
            return "user", session_id, environment_id
        
        if instance_hostname is not None:
            return "instance", session_id, None
        
        return None, session_id, None

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