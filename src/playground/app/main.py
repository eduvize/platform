import logging
import os
from .config import get_jwt_signing_key, get_environment_id
from .client import connect_to_server
from .jwt import create_token

logging.basicConfig(level=logging.INFO)

def initialize_session():
    pod_hostname = os.getenv("HOSTNAME")
    session_id = os.getenv("SESSION_ID")

    signing_key = get_jwt_signing_key()
    
    logging.info("Generating token")
        
    logging.info("Connecting to server")
    token = create_token(
        data={
            "session_id": session_id,
            "environment_id": get_environment_id(),
            "hostname": pod_hostname
        }, 
        secret=signing_key, 
        expiration_minutes=5
    )
    connect_to_server(token)