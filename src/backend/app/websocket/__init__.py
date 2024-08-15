from typing import Optional
from socketio import AsyncServer
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

socket = AsyncServer(async_mode="asgi", cors_allowed_origins="*")

@socket.event
async def connect(sid: str, environment_data: dict, extra: Optional[dict] = None):
    token = get_token(environment_data)
    
    if token is None:
        logger.info(f"Connection from {sid} failed due to missing token")
        return False
    
    logger.info(f"Connection from {sid} succeeded with token {token}")
    
    return True

def get_token(environ: dict) -> Optional[str]:
    """
    Extracts the token from the header information associated with the connect event

    Args:
        environ (dict): The environment data from the websocket connection

    Returns:
        Optional[str]: The token if it exists
    """
    scope = environ.get("asgi.scope", None)
    
    if scope is None:
        return None
    
    headers = scope.get("headers", None)
    
    if headers is None:
        return None
    
    return next((
        header[1].decode().strip("Bearer ") 
        for header in headers 
        if header[0].decode() == "authorization"
    ), None)