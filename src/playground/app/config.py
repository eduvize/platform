import os
from dotenv import load_dotenv

load_dotenv()

def get_api_base_url() -> str:
    return os.getenv("BASE_API_URL")

def get_basic_auth_username() -> str:
    return os.getenv("BASIC_AUTH_USERNAME")

def get_basic_auth_password() -> str:
    return os.getenv("BASIC_AUTH_PASSWORD")

def get_session_id_path() -> str:
    return os.getenv("SESSION_ID_PATH", "/playground/session_id.txt")