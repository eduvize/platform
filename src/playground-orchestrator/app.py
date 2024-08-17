import os
import requests
import time
import logging
import signal
import sys
import uuid
from typing import Optional
from datetime import datetime
from sqlmodel import Field, create_engine, Session, select
from sqlmodel import SQLModel
from kubernetes import client, config
from requests.auth import HTTPBasicAuth
from sqlalchemy import func

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Database model for the playground_sessions table
class PlaygroundSession(SQLModel, table=True):
    __tablename__ = "playground_sessions"
    
    id: uuid.UUID                       = Field(default_factory=uuid.uuid4, primary_key=True)
    type: str                           = Field(nullable=False)
    instance_hostname: Optional[str]    = Field(nullable=True)
    created_at_utc: datetime            = Field(default_factory=datetime.utcnow)

def get_db_session():
    connection_string = os.getenv("POSTGRES_CONNECTION_STRING")
    engine = create_engine(connection_string)
    session = Session(engine)
    return session

def get_waiting_session_count():
    session = get_db_session()
    statement = select(func.count(PlaygroundSession.id)).where(PlaygroundSession.instance_hostname == None)
    result = session.exec(statement).one()
    session.close()
    logging.info(f"Retrieved session count: {result}")
    return result

def get_session_count():
    session = get_db_session()
    statement = select(func.count(PlaygroundSession.id))
    result = session.exec(statement).one()
    session.close()
    logging.info(f"Retrieved session count: {result}")
    return result

def get_reserved_sessions():
    session = get_db_session()
    statement = select(PlaygroundSession).where(PlaygroundSession.instance_hostname != None)
    result = session.exec(statement).all()
    session.close()
    return result

def get_pod_count(namespace: str, label_selector: str):
    config.load_incluster_config()
    v1 = client.CoreV1Api()
    pods = v1.list_namespaced_pod(namespace, label_selector=label_selector)
    
    # Get pods that have been assigned a session
    pods_with_session_label = [pod for pod in pods.items if pod.status.phase != "Terminating" and pod.metadata.labels.get("playground-session-id")]
    
    # Get running or pending pods that do not have a session
    pending_pods = [pod for pod in pods.items if (pod.status.phase == "Pending" or pod.status.phase == "Running") and not pod.metadata.labels.get("playground-session-id")]
    
    return len(pods_with_session_label), len(pending_pods)

def get_pods_with_sessions(namespace: str):
    """
    Returns a list of pods that have been assigned a session label along with the session ID.

    Args:
        namespace (str): The namespace to search for pods in.
        
    Returns:
        list: A list of dictionaries containing the pod name and session ID.
    """
    
    config.load_incluster_config()
    v1 = client.CoreV1Api()
    pods = v1.list_namespaced_pod(namespace, label_selector="app=playground")
    pods_with_sessions = []
    
    for pod in pods.items:
        session_id = pod.metadata.labels.get("playground-session-id")
        
        if session_id:
            pods_with_sessions.append({"name": pod.metadata.name, "session_id": session_id})
    
    return pods_with_sessions

def scale_deployment(namespace: str, deployment_name: str, replicas: int):
    config.load_incluster_config()
    apps_v1 = client.AppsV1Api()
    deployment = apps_v1.read_namespaced_deployment(name=deployment_name, namespace=namespace)
    
    # Calculate the desired number of replicas
    desired_replicas = max(deployment.spec.replicas + replicas, 0)  # Ensure replicas are >= 0
    
    if desired_replicas != deployment.spec.replicas:
        deployment.spec.replicas = desired_replicas
        apps_v1.patch_namespaced_deployment(name=deployment_name, namespace=namespace, body=deployment)
        logging.info(f"Scaled deployment '{deployment_name}' to {desired_replicas} replicas")
    else:
        logging.info(f"No scaling action taken for deployment '{deployment_name}'; replicas already at desired count ({desired_replicas})")

def terminate_pod(namespace: str, pod_name: str):
    config.load_incluster_config()
    api_base_url = os.getenv("API_BASE_URL")
    username = os.getenv("BASIC_AUTH_USERNAME")
    password = os.getenv("BASIC_AUTH_PASSWORD")
    url = f"{api_base_url}/playground/internal/session"

    try:
        logging.info(f"Attempting to call cleanup API for pod {pod_name}")
        response = requests.delete(url, json={"hostname": pod_name}, auth=HTTPBasicAuth(username, password))
        response.raise_for_status()
        logging.info(f"Successfully called cleanup API for pod {pod_name}")
    except requests.RequestException as e:
        logging.error(f"Failed to call cleanup API for pod {pod_name}: {e}")
    
    v1 = client.CoreV1Api()
    v1.delete_namespaced_pod(pod_name, namespace)

def delete_ready_pods(namespace: str):
    config.load_incluster_config()
    v1 = client.CoreV1Api()
    pods = v1.list_namespaced_pod(namespace, label_selector="ready-for-deletion=true")
    scale_down_count = 0

    if pods.items:  # Ensure pods.items is not None
        for pod in pods.items:
            terminate_pod(namespace, pod.metadata.name)
            scale_down_count += 1

    if scale_down_count > 0:
        scale_deployment(namespace, "playground", replicas=-scale_down_count)

def graceful_shutdown(signum, frame):
    logging.info("Received termination signal. Performing graceful shutdown...")
    sys.exit(0)

def main():
    namespace = "eduvize"
    label_selector = "app=playground"
    deployment_name = "playground"
    interval_seconds = int(os.getenv("SCALING_INTERVAL_SECONDS", "5"))

    logging.info("Starting the scaling process")
    
    # Register signal handlers for graceful shutdown
    signal.signal(signal.SIGTERM, graceful_shutdown)
    signal.signal(signal.SIGINT, graceful_shutdown)

    while True:
        try:
            total_session_count = get_session_count()
            waiting_session_count = get_waiting_session_count()
            session_pods, pending_pods = get_pod_count(namespace, label_selector)
            total_pods = session_pods + pending_pods

            # Make sure there are enough pods to handle the waiting sessions
            if waiting_session_count > 0:
                if pending_pods < waiting_session_count:
                    scale_deployment(namespace, deployment_name, replicas=waiting_session_count)

            if total_pods > total_session_count:
                session_pods = get_pods_with_sessions(namespace)
                reserved_sessions = get_reserved_sessions()
                unneeded_count = 0
                
                # Delete any pods that have a session that's no longer in the database
                for pod in session_pods:
                    if not any(str(session.id) == pod["session_id"] for session in reserved_sessions):
                        terminate_pod(namespace, pod["name"])
                        
                        unneeded_count += 1

                if unneeded_count > 0:
                    scale_deployment(namespace, deployment_name, replicas=-unneeded_count)
                    
            # Delete pods that are ready for deletion
            delete_ready_pods(namespace)
        except Exception as e:
            logging.error(f"An error occurred during the scaling process: {e}")
        
        logging.info(f"Sleeping for {interval_seconds} seconds before next check")
        time.sleep(interval_seconds)

if __name__ == "__main__":
    main()
