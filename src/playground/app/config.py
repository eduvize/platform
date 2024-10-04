import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

def get_backend_api_endpoint() -> str:
    return os.getenv("BACKEND_API_ENDPOINT")

def get_backend_socketio_endpoint() -> str:
    return os.getenv("BACKEND_SOCKETIO_ENDPOINT")

def get_jwt_signing_key() -> str:
    return os.getenv("JWT_SIGNING_KEY")

def get_max_wait_time() -> int:
    return int(os.getenv("MAX_WAIT_TIME", 10))

def get_self_destruct_enabled() -> bool:
    return os.getenv("ENABLE_SELF_DESTRUCT", "true").lower() == "true"

def get_purge_on_disconnect() -> bool:
    return os.getenv("PURGE_DATA_ON_DISCONNECT", "false").lower() == "true"

def get_session_id() -> str:
    return os.getenv("SESSION_ID")

def get_environment_id() -> Optional[str]:
    return os.getenv("ENVIRONMENT_ID", None)

def get_image_tag() -> Optional[str]:
    return os.getenv("IMAGE_TAG", None)

def get_openai_key() -> str:
    return os.getenv("OPENAI_KEY")