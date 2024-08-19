import os
from typing import Optional
from dotenv import load_dotenv
from sqlalchemy import Boolean

load_dotenv()

# App
def get_public_ui_url() -> str:
    return os.getenv("PUBLIC_UI_URL")

def get_public_url() -> str:
    return os.getenv("PUBLIC_URL")

def get_dashboard_endpoint() -> str:
    return os.getenv("DASHBOARD_ENDPOINT")

def get_app_port() -> int:
    return os.getenv("PORT", 8000)

def get_live_reload() -> Boolean:
    str_value = os.getenv("ENABLE_LIVE_RELOAD", "true")
    return str_value.lower() == "true"

# AWS
def get_aws_access_key() -> str:
    return os.getenv("AWS_ACCESS_KEY")

def get_aws_secret_key() -> str:
    return os.getenv("AWS_SECRET_KEY")

# Database
def get_database_connection_string(driver: Optional[str] = None) -> str:
    DRIVER = f"postgresql+{driver}" if driver is not None else "postgresql"
    DB_HOST = os.getenv("POSTGRES_HOST", "localhost")
    DB_USER = os.getenv("POSTGRES_USER")
    DB_PASSWORD = os.getenv("POSTGRES_PASSWORD")
    DB_NAME = os.getenv("POSTGRES_DB")

    return f"{DRIVER}://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"

# Access tokens
def get_token_expiration_minutes() -> int:
    return int(os.getenv("TOKEN_EXPIRATION_MINUTES", "10"))

def get_refresh_token_expiration_days() -> int:
    return int(os.getenv("REFRESH_TOKEN_EXPIRATION_DAYS", "7"))

def get_token_secret() -> str:
    return os.getenv("TOKEN_SECRET", "secret")

def get_playground_token_secret() -> str:
    return os.getenv("PLAYGROUND_TOKEN_SECRET", "secret")

# S3 / Min.io
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

# Redis / Cache
def get_redis_host() -> str:
    return os.getenv("REDIS_HOST")

# Email
def get_mailgun_key() -> str:
    return os.getenv("MAILGUN_API_KEY")

def get_email_noreply_address() -> str:
    return os.getenv("NOREPLY_ADDRESS")

# OpenAI
def get_openai_key() -> str:
    return os.getenv("OPENAI_KEY")

# GitHub
def get_github_client_id() -> str:
    return os.getenv("GITHUB_CLIENT_ID")

def get_github_client_secret() -> str:
    return os.getenv("GITHUB_CLIENT_SECRET")

# Google
def get_google_client_id() -> str:
    return os.getenv("GOOGLE_CLIENT_ID")

def get_google_client_secret() -> str:
    return os.getenv("GOOGLE_CLIENT_SECRET")

def get_auth_redirect_url() -> str:
    return os.getenv("AUTH_REDIRECT_URL")