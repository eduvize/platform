import os
import time
import logging
import signal
import sys
import uuid
from kubernetes import client, config
from .database import get_reserved_sessions, get_unreserved_sessions, assign_session, unassign_session, remove_session
from .pod_creation import create_new_pod

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load the Kubernetes configuration
config.load_incluster_config()

def get_pods():
    """
    Gets all playground pods in the eduvize namespace

    Returns:
        list: A list of playground pods
    """
    
    v1 = client.CoreV1Api()
    pods = v1.list_namespaced_pod("eduvize", label_selector="app=playground")
    pod_list = []
    
    for pod in pods.items:
        pod_list.append({
            "name": pod.metadata.name,
            "session_id": pod.metadata.labels.get("playground-session-id")
        })
        
    return pod_list

def terminate_pod(pod_name: str):
    v1 = client.CoreV1Api()
    v1.delete_namespaced_pod(pod_name, "eduvize")

def get_pods_ready_for_self_destruction():
    """
    Returns a list of pods that have marked themselves for deletion (user no longer present)
    """
    v1 = client.CoreV1Api()
    pods = v1.list_namespaced_pod("eduvize", label_selector="ready-for-deletion=true,app=playground")
    pod_list = []
    
    if pods.items:  # Ensure pods.items is not None
        for pod in pods.items:
            pod_list.append({
                "name": pod.metadata.name,
                "session_id": pod.metadata.labels.get("playground-session-id")
            })
                
    return pod_list

def graceful_shutdown(signum, frame):
    logging.info("Received termination signal. Performing graceful shutdown...")
    sys.exit(0)

def main():
    interval_seconds = int(os.getenv("SCALING_INTERVAL_SECONDS", "5"))

    logging.info("Starting the scaling process")
    
    # Register signal handlers for graceful shutdown
    signal.signal(signal.SIGTERM, graceful_shutdown)
    signal.signal(signal.SIGINT, graceful_shutdown)

    while True:
        reserved_sessions = get_reserved_sessions()
        unreserved_sessions = get_unreserved_sessions()
        self_destruct_pods = get_pods_ready_for_self_destruction()
        pods = get_pods()
        
        # Loop through active pods and terminate any that are not in the reserved sessions
        for pod in pods:
            if not any(str(session.id) == pod["session_id"] for session in reserved_sessions):
                logging.info(f"Found a pod without a corresponding session: {pod['session_id']}")
                terminate_pod(pod["name"])
                logging.info(f"Terminated pod {pod['name']} due to missing session")
            
        # Loop through each reserved sessions and check if there is a corresponding pod
        for session in reserved_sessions:
            if not any(str(session.id) == pod["session_id"] for pod in pods):
                logging.info(f"Found a session without a corresponding pod: {session.id}")
                unassign_session(session.id)
                logging.info(f"Unassigned session {session.id}, waiting for it to be reassigned")
                break
        
        # Loop through each unreserved session and create a pod
        for session in unreserved_sessions:
            logging.info(f"Creating a new pod for session {session.id}")
            pod_name = create_new_pod(str(session.id), session.type)
            assign_session(session.id, pod_name)
            logging.info(f"Assigned session {session.id} to pod {pod_name}")

        # Loop through pods and check if there is a corresponding session
        for pod in pods:
            if not any(str(session.id) == pod["session_id"] for session in reserved_sessions):
                logging.info(f"Found a pod without a corresponding session: {pod['session_id']}")
                terminate_pod(pod["name"])
                logging.info(f"Terminated pod {pod['name']} due to missing session")

        # Delete pods that are ready for deletion
        for pod in self_destruct_pods:
            terminate_pod(pod["name"])
            remove_session(uuid.UUID(pod["session_id"]))
            logging.info(f"Terminated pod {pod['name']} due to self-destruction")
                
        logging.info(f"Sleeping for {interval_seconds} seconds before next check")
        time.sleep(interval_seconds)