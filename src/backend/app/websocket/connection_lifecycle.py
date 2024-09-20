import logging
from app.repositories import PlaygroundRepository
from socketio import AsyncServer
from common.cache import delete_key, get_key, set_key
from .cache_keys import get_image_tag_cache_key, get_liveness_cache_key, get_instance_ready_cache_key, get_user_connected_cache_key
logger = logging.getLogger(__name__)

async def handle_user_connection(
    server: AsyncServer,
    playground_repo: PlaygroundRepository, 
    sid: str, 
    user_id: str, 
    session_id: str, 
    environment_id: str
):
    if environment_id is None:
        logger.info(f"Connection from {sid} failed due to missing environment ID")
        return False
    
    logger.info(f"Connection from {sid} succeeded with user ID {user_id}, session ID {session_id}")
    
    async with server.session(sid) as session:
        session["session_id"] = session_id
        session["user_id"] = user_id
        session["environment_id"] = environment_id
    
    logger.info(f"User wants environment {environment_id}")
    
    environment = playground_repo.get_environment(environment_id)

    if environment is None:
        logger.info(f"Connection from {sid} failed due to missing environment {environment_id}")
        return False
    
    logger.info(f"Image tag for environment {environment_id}: {environment.image_tag}")
    
    image_tag = environment.image_tag
    
    if image_tag is None:
        logger.info(f"Connection from {sid} failed due to missing image tag for environment {environment_id}")
        return False
    
    set_key(
        key=get_image_tag_cache_key(environment_id),
        value=image_tag
    )
    
    is_alive = get_key(get_liveness_cache_key(session_id))
    is_ready = get_key(get_instance_ready_cache_key(session_id))
    
    # Check if the instance is already waiting for the user
    if is_alive is not None:
        await server.emit("instance_connected", room=session_id) # Notify the user of the instance connection
        await server.emit("user_connected", {
            "image_tag": image_tag
        }, room=session_id) # Notify the instance of the user connection
        
    if is_ready is not None:
        await server.emit("instance_ready", room=session_id)
        
    connected_key = get_user_connected_cache_key(session_id)
    
    set_key(
        key=connected_key,
        value="1",
        expiration=5 * 60 # 5 minutes
    )
    
async def handle_instance_connection(
    server: AsyncServer,
    sid: str, 
    session_id: str, 
    environment_id: str, 
    instance_hostname: str
):
    logger.info(f"Connection from {sid} succeeded with hostname {instance_hostname}, session ID {session_id}")
    
    async with server.session(sid) as session:
        session["session_id"] = session_id
        session["instance_hostname"] = instance_hostname
        
    user_connected_key = get_user_connected_cache_key(session_id)
    image_tag_key = get_image_tag_cache_key(environment_id)
    
    is_user_connected = get_key(user_connected_key)
    image_tag = get_key(image_tag_key)
    
    if is_user_connected is not None and image_tag is not None:
        await server.emit("user_connected", {
            "image_tag": image_tag
        }, room=session_id) # Notify the instance of the user connection
        
    set_key(
        key=get_liveness_cache_key(session_id),
        value="1",
        expiration=5 * 60 # 5 minutes
    )
    
    await server.emit("instance_connected", room=session_id) # Notify the user of the instance connection
    
async def handle_user_disconnect(server: AsyncServer, sid: str, session_id: str, environment_id: str):
    logger.info(f"User {session_id} disconnected")
    image_cache_key = get_image_tag_cache_key(environment_id)
    await server.emit("user_disconnected", room=session_id, skip_sid=sid)
    delete_key(get_user_connected_cache_key(session_id))
    delete_key(image_cache_key)
    
async def handle_instance_disconnect(server: AsyncServer, sid: str, session_id: str):
    logger.info(f"Instance {session_id} disconnected")
    await server.emit("instance_disconnected", room=session_id, skip_sid=sid)
    delete_key(get_liveness_cache_key(session_id))
    delete_key(get_instance_ready_cache_key(session_id))