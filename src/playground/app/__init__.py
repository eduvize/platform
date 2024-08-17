import os
from .server import app
from .orchestration import create_reservation, validate_reservation, kill_pod, set_session_label
from .config import get_session_id_path

def initialize_session():
    pod_hostname = os.getenv("HOSTNAME")

    print(f"Hostname: {pod_hostname}")

    session = create_reservation(pod_hostname)

    if session == None:
        print("Failed to create reservation")
        
        kill_pod()
        exit(1)
        
    set_session_label(session.session_id)
        
    with open(get_session_id_path(), "w") as f:
        f.write(session.session_id)
        
    print("Session initialized")