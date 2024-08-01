import os
from dotenv import load_dotenv
from sqlalchemy import Boolean

load_dotenv()

def get_database_connection_string() -> str:
    DB_HOST = os.getenv("POSTGRES_HOST", "localhost")
    DB_USER = os.getenv("POSTGRES_USER")
    DB_PASSWORD = os.getenv("POSTGRES_PASSWORD")
    DB_NAME = os.getenv("POSTGRES_DB")

    return f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"

def get_app_port() -> int:
    return os.getenv("PORT", 8000)

def get_live_reload() -> Boolean:
    str_value = os.getenv("ENABLE_LIVE_RELOAD", "true")
    return str_value.lower() == "true"

def get_token_expiration() -> int:
    return int(os.getenv("TOKEN_EXPIRATION", "15"))

def get_token_secret() -> str:
    return os.getenv("TOKEN_SECRET", "secret")

def get_s3_endpoint() -> str:
    return os.getenv("S3_ENDPOINT")

def get_s3_public_endpoint() -> str:
    return os.getenv("S3_PUBLIC_ENDPOINT")

def get_s3_avatar_bucket() -> str:
    return os.getenv("S3_BUCKET")

def get_s3_access_key() -> str:
    return os.getenv("S3_ACCESS_KEY")

def get_s3_secret_key() -> str:
    return os.getenv("S3_SECRET_KEY")