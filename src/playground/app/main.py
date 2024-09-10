import logging
import os
import time
from .config import get_jwt_signing_key, get_purge_on_disconnect
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
        token = create_token(
            data={
                "session_id": session_id,
                "hostname": pod_hostname
            }, 
            secret=signing_key, 
            expiration_minutes=5
        )
        
        # Loop until /userland/NOTICE.txt is found
        while True:
            try:
                with open("/userland/NOTICE.txt") as f:
                    break
            except Exception:
                print("Waiting for NOTICE.txt")
                pass
            
            time.sleep(1)
        
        logging.info("Connecting to server")
        connect_to_server(token)
        
        if get_purge_on_disconnect():
            logging.info("Reinitializing environment")
            reinitialize_environment()
            
            logging.info("Reinitializing session")
        else:
            break