import logging
from typing import Literal, Optional, Tuple
from socketio import AsyncServer, AsyncNamespace
from app.repositories import PlaygroundRepository
from app.utilities.jwt import decode_token, InvalidJWTToken
from config import get_playground_token_secret
from .connection_lifecycle import handle_instance_connection, handle_user_connection, handle_instance_disconnect, handle_user_disconnect, handle_instance_ready
from ..util import get_token_from_environ

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

socket_server = AsyncServer(async_mode="asgi", cors_allowed_origins="*", async_handlers=True)

class PlaygroundNamespace(AsyncNamespace):
    def __init__(self, namespace):
        super().__init__(namespace)

    async def on_connect(self, sid: str, environ: dict):
        token = get_token_from_environ(environ)
        
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
            await self.enter_room(sid, session_id)
            
            # If it's a user
            if user_id is not None:
                playground_repo = PlaygroundRepository()
                await handle_user_connection(
                    server=self, 
                    playground_repo=playground_repo, 
                    sid=sid, 
                    user_id=user_id, 
                    session_id=session_id, 
                    environment_id=environment_id
                )
                    
            # If it's an instance
            if instance_hostname is not None:
                await handle_instance_connection(
                    server=self,
                    sid=sid, 
                    session_id=session_id, 
                    environment_id=environment_id, 
                    instance_hostname=instance_hostname
                )
            
            # Store connection information in the session
            await self.save_session(sid, {
                "session_id": session_id,
                "user_id": user_id,
                "instance_hostname": instance_hostname,
                "environment_id": environment_id
            })
            
        except InvalidJWTToken:
            logger.info(f"Connection from {sid} failed due to invalid token")
            logger.info(f"Token: {token}")
            return False
        
        return True

    async def on_setup_status(self, sid: str, status: str):
        client_type, session_id, environment_id = await get_connection_information(self, sid)
        
        if client_type == "instance" and session_id:
            logger.info(f"Received setup status from {client_type} {session_id}: {status}")
            
            await self.emit("setup_status", status, room=session_id, skip_sid=sid)

    async def on_ready(self, sid: str):
        client_type, session_id, env_id = await get_connection_information(self, sid)
        
        if client_type == "instance" and session_id:
            logger.info(f"Instance {session_id} is ready")
            
            await handle_instance_ready(
                server=self,
                sid=sid,
                session_id=session_id
            )

    async def on_disconnect(self, sid: str):
        client_type, session_id, environment_id = await get_connection_information(self, sid)
        
        if client_type and session_id:
            if client_type == "instance":
                await handle_instance_disconnect(
                    server=self,
                    sid=sid,
                    session_id=session_id,
                )
                
            if client_type == "user":
                await handle_user_disconnect(
                    server=self,
                    sid=sid,
                    session_id=session_id,
                    environment_id=environment_id
                )

    async def on_terminal_input(self, sid: str, t_input: str):
        client_type, session_id, env_id = await get_connection_information(self, sid)
        
        if client_type == "user" and session_id:
            logger.info(f"Received terminal input from {client_type} {session_id}: {t_input}")
            
            await self.emit("terminal_input", t_input, room=session_id, skip_sid=sid)

    async def on_terminal_output(self, sid: str, output: str):
        client_type, session_id, env_id = await get_connection_information(self, sid)
        
        if client_type == "instance" and session_id:
            logger.info(f"Sending terminal output to {client_type} {session_id}: {output}")
            
            await self.emit("terminal_output", output, room=session_id, skip_sid=sid)

    async def on_terminal_resize(self, sid: str, data: dict):
        client_type, session_id, env_id = await get_connection_information(self, sid)
        
        if client_type == "user" and session_id:
            logger.info(f"Resizing terminal for {client_type} {session_id} to {data['rows']}x{data['columns']}")
            
            await self.emit("terminal_resize", data, room=session_id, skip_sid=sid)

    async def on_create(self, sid: str, data: dict):
        client_type, session_id, env_id = await get_connection_information(self, sid)
        
        if client_type == "user" and session_id:
            logger.info(f"Creating new filesystem entry for {client_type} {session_id}: {data['type']}, {data['path']}")
            
            await self.emit("create", data, room=session_id, skip_sid=sid)

    async def on_rename(self, sid: str, data: dict):
        client_type, session_id, env_id = await get_connection_information(self, sid)
        
        if client_type == "user" and session_id:
            logger.info(f"Renaming filesystem entry for {client_type} {session_id}: {data['path']}, {data['new_path']}")
            
            await self.emit("rename", data, room=session_id, skip_sid=sid)

    async def on_delete(self, sid: str, data: dict):
        client_type, session_id, env_id = await get_connection_information(self, sid)
        
        if client_type == "user" and session_id:
            logger.info(f"Deleting filesystem entry for {client_type} {session_id}: {data['path']}")
            
            await self.emit("delete", data, room=session_id, skip_sid=sid)

    async def on_environment(self, sid: str, data: dict):
        client_type, session_id, env_id = await get_connection_information(self, sid)
        
        if client_type == "instance" and session_id:
            logger.info(f"Updating environment for {client_type} {session_id}")
            
            await self.emit("environment", data, room=session_id, skip_sid=sid)

    async def on_open_file(self, sid: str, data: dict):
        client_type, session_id, env_id = await get_connection_information(self, sid)
        
        if client_type == "user" and session_id:
            logger.info(f"Opening file {data['path']} for {client_type} {session_id}")
            
            await self.emit("open_file", data, room=session_id, skip_sid=sid)

    async def on_save_file(self, sid: str, data: dict):
        client_type, session_id, env_id = await get_connection_information(self, sid)
        
        if client_type == "user" and session_id:
            logger.info(f"Saving file {data['path']} for {client_type} {session_id}")
            
            await self.emit("save_file", data, room=session_id, skip_sid=sid)

    async def on_file_content(self, sid: str, data: dict):
        client_type, session_id, env_id = await get_connection_information(self, sid)
        
        if client_type == "instance" and session_id:
            logger.info(f"Sending file content to user for {data['path']} in session {session_id}")
            
            await self.emit("file_content", data, room=session_id, skip_sid=sid)

    async def on_subscribe_to_path(self, sid: str, data: dict):
        client_type, session_id, env_id = await get_connection_information(self, sid)
        
        if client_type == "user" and session_id:
            logger.info(f"Subscribing to path {data['path']} in session {session_id}")
            
            await self.emit("subscribe_to_path", data, room=session_id, skip_sid=sid)

    async def on_unsubscribe_from_path(self, sid: str, data: dict):
        client_type, session_id, env_id = await get_connection_information(self, sid)
        
        if client_type == "user" and session_id:
            logger.info(f"Unsubscribing from path {data['path']} in session {session_id}")
            
            await self.emit("unsubscribe_from_path", data, room=session_id, skip_sid=sid)

    async def on_get_directory(self, sid: str, data: dict):
        client_type, session_id, env_id = await get_connection_information(self, sid)
        
        if client_type == "user" and session_id:
            logger.info(f"Getting directory for {data['path']} in session {session_id}")
            
            await self.emit("get_directory", data, room=session_id, skip_sid=sid)

    async def on_directory_contents(self, sid: str, data: dict):
        client_type, session_id, env_id = await get_connection_information(self, sid)
        
        if client_type == "instance" and session_id:
            logger.info(f"Sending directory contents to user for {data['path']} in session {session_id}")
            
            await self.emit("directory_contents", data, room=session_id, skip_sid=sid)

    async def on_exercise_objective_status(self, sid: str, data: dict):
        client_type, session_id, env_id = await get_connection_information(self, sid)
        
        if client_type == "instance" and session_id:
            logger.info(f"Updating exercise objective status for {data['objective_id']} in session {session_id}")
            
            await self.emit("exercise_objective_status", data, room=session_id, skip_sid=sid)
            
async def get_connection_information(namespace: AsyncNamespace, sid: str) -> Tuple[Literal["user", "instance", None], Optional[str], Optional[str]]:
    """
    Gets the client type and session ID associated with a socket connection.

    Returns:
        Tuple[Literal["user", "instance", None], str]: The client type and session ID.
    """
    session = await namespace.get_session(sid)
    session_id = session.get("session_id", None)
    user_id = session.get("user_id", None)
    instance_hostname = session.get("instance_hostname", None)
    environment_id = session.get("environment_id", None)
    
    if user_id is not None:
        return "user", session_id, environment_id
    
    if instance_hostname is not None:
        return "instance", session_id, None
    
    return None, session_id, None