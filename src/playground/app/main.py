import logging
import os
import time
from .config import get_jwt_signing_key, get_purge_on_disconnect, get_environment_id
from .client import connect_to_server
from .jwt import create_token
from .cleanup import reinitialize_environment

logging.basicConfig(level=logging.INFO)

def initialize_session():
    pod_hostname = os.getenv("HOSTNAME")
    session_id = os.getenv("SESSION_ID")

    print(f"Hostname: {pod_hostname}")
    
    signing_key = get_jwt_signing_key()
    
    while True:
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
        
        if get_purge_on_disconnect():
            logging.info("Reinitializing environment")
            reinitialize_environment()
            
            logging.info("Reinitializing session")
        else:
            break