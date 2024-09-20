def get_liveness_cache_key(session_id: str) -> str:
    """
    Generates a cache key for the liveness status of a session instance.

    Args:
        session_id (str): The ID of the session to generate the key for.

    Returns:
        str: The cache key.
    """
    return f"playground_session:{session_id}:alive"

def get_instance_ready_cache_key(session_id: str) -> str:
    """
    Generates a cache key for the readiness status of a session instance.

    Args:
        session_id (str): The ID of the session to generate the key for.

    Returns:
        str: The cache key.
    """
    return f"playground_session:{session_id}:ready"

def get_user_connected_cache_key(session_id: str) -> str:
    """
    Generates a cache key for the user connected status of a session instance.

    Args:
        session_id (str): The ID of the session to generate the key for.

    Returns:
        str: The cache key.
    """
    return f"playground_session:{session_id}:user_connected"

def get_image_tag_cache_key(environment_id: str) -> str:
    """
    Generates a cache key for the image tag of an environment.

    Args:
        environment_id (str): The ID of the environment to generate the key for.

    Returns:
        str: The cache key.
    """
    return f"playground_environment:{environment_id}:image_tag"