import logging
from app.repositories import PlaygroundRepository
from socketio import AsyncServer
from common.cache import delete_key, get_key, set_key
from domain.enums.playground_enums import EnvironmentType
from .cache_keys import (
    get_image_tag_cache_key, 
    get_liveness_cache_key, 
    get_instance_ready_cache_key, 
    get_user_connected_cache_key,
    get_environment_id_cache_key
)

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
    
    if environment.image_tag is None:
        logger.info(f"Connection from {sid} failed due to missing image tag for environment {environment_id}")
        return False

    if environment.type is None:
        logger.info(f"Connection from {sid} failed due to missing type for environment {environment_id}")
        return False
    
    if environment.resource_id is None:
        logger.info(f"Connection from {sid} failed due to missing resource ID for environment {environment_id}")
        return False
    
    environment_id_cache_key = get_environment_id_cache_key(session_id)
    image_cache_key = get_image_tag_cache_key(environment_id)
    
    await set_key(
        key=environment_id_cache_key,
        value=environment_id
    )
    
    await set_key(
        key=image_cache_key,
        value=environment.image_tag
    )
    
    is_alive = await get_key(get_liveness_cache_key(session_id))
    is_ready = await get_key(get_instance_ready_cache_key(session_id))
    
    # Check if the instance is already waiting for the user
    if is_alive is not None:
        logger.info(f"Instance {session_id} is already alive")
        await server.emit("instance_connected", room=session_id) # Notify the user of the instance connection
        await server.emit("user_connected", {
            "image_tag": environment.image_tag
        }, room=session_id) # Notify the instance of the user connection
        
        # Tell the instance to start monitoring the exercise
        if environment.type == EnvironmentType.EXERCISE.value:
            logger.info(f"Starting exercise monitoring for environment {environment_id}")
            await server.emit("start_exercise_monitoring", {
                "exercise_id": str(environment.resource_id)
            }, room=session_id)
        
    if is_ready is not None:
        logger.info(f"Instance {session_id} is already ready")
        await server.emit("instance_ready", room=session_id)
        
    connected_key = get_user_connected_cache_key(session_id)
    
    await set_key(
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
        session["environment_id"] = environment_id
        session["instance_hostname"] = instance_hostname
    
    if environment_id:
        user_connected_key = get_user_connected_cache_key(session_id)
        image_tag_key = get_image_tag_cache_key(environment_id)
        
        is_user_connected = await get_key(user_connected_key)
        image_tag = await get_key(image_tag_key)
        
        if is_user_connected is not None and image_tag is not None:
            await server.emit("user_connected", {
                "image_tag": image_tag
            }, room=session_id) # Notify the instance of the user connection
        
    await set_key(
        key=get_liveness_cache_key(session_id),
        value="1"
    )
    
    await server.emit("instance_connected", room=session_id) # Notify the user of the instance connection

async def handle_instance_ready(server: AsyncServer, sid: str, session_id: str):
    logger.info(f"Instance {session_id} is ready")
    
    async with server.session(sid) as session:
        environment_id = session.get("environment_id")
        
        if not environment_id:
            provided_environment_id_cache_key = get_environment_id_cache_key(session_id)
            environment_id = await get_key(provided_environment_id_cache_key)
        
        if not environment_id:
            logger.error(f"Instance {session_id} is ready, but no environment ID was found")
            return
        
        playground_repo = PlaygroundRepository()
        environment = playground_repo.get_environment(environment_id)
        
        if environment is None:
            logger.error(f"Instance {session_id} is ready, but no environment was found for ID {environment_id}")
            return        
        
        logger.info(f"Instance {session_id} is ready for environment {environment_id} of type {environment.type} with resource ID {environment.resource_id}")
        
        # Tell the instance to start monitoring the exercise
        if environment.type == EnvironmentType.EXERCISE:
            await server.emit("start_exercise_monitoring", {
                "exercise_id": str(environment.resource_id)
            }, room=session_id)
            
        await server.emit("instance_ready", room=session_id, skip_sid=sid)
        
        await set_key(
            key=get_instance_ready_cache_key(session_id),
            value="1"
        )

async def handle_user_disconnect(server: AsyncServer, sid: str, session_id: str, environment_id: str):
    logger.info(f"User {session_id} disconnected")
    image_cache_key = get_image_tag_cache_key(environment_id)
    instance_ready_key = get_instance_ready_cache_key(session_id)
    await server.emit("user_disconnected", room=session_id, skip_sid=sid)
    await delete_key(get_user_connected_cache_key(session_id))
    await delete_key(image_cache_key)
    await delete_key(instance_ready_key)
    
async def handle_instance_disconnect(server: AsyncServer, sid: str, session_id: str):
    logger.info(f"Instance {session_id} disconnected")
    await server.emit("instance_disconnected", room=session_id, skip_sid=sid)
    await delete_key(get_liveness_cache_key(session_id))
    await delete_key(get_instance_ready_cache_key(session_id))