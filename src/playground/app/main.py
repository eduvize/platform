import os
import time
from .config import get_jwt_signing_key
from .client import connect_to_server
from .jwt import create_token

def initialize_session():
    pod_hostname = os.getenv("HOSTNAME")
    session_id = os.getenv("SESSION_ID")

    print(f"Hostname: {pod_hostname}")
    
    signing_key = get_jwt_signing_key()
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
    
    connect_to_server(token)