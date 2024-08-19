import os
from typing import Optional

def get_playground_controller_image() -> str:
    """
    Gets the playground controller image

    Returns:
        str: The playground controller image
    """
    
    return os.getenv("PLAYGROUND_CONTROLLER_IMAGE")

def get_environment_image(instance_type: str) -> str:
    """
    Gets the environment image for a given instance type

    Args:
        instance_type (str): The instance type

    Returns:
        str: The environment image
    """
    image_prefix = os.getenv("PLAYGROUND_ENVIRONMENT_IMAGE_PREFIX")
    
    return f"{image_prefix}-{instance_type.lower()}:latest"

def get_backend_socketio_endpoint() -> str:
    """
    Gets the backend socket.io endpoint

    Returns:
        str: The backend socket.io endpoint
    """
    
    return os.getenv("BACKEND_SOCKETIO_ENDPOINT")

def get_jwt_signing_key() -> str:
    """
    Gets the JWT signing key

    Returns:
        str: The JWT signing key
    """
    
    return os.getenv("JWT_SIGNING_KEY")

def get_termination_grace_period() -> int:
    """
    Gets the termination grace period

    Returns:
        int: The termination grace period
    """
    
    return int(os.getenv("TERMINATION_GRACE_PERIOD", "5"))

def get_image_pull_secret() -> Optional[str]:
    """
    Gets the image pull secret

    Returns:
        Optional[str]: The image pull secret
    """
    
    return os.getenv("IMAGE_PULL_SECRET", None)