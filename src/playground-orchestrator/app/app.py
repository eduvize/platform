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
from kubernetes.client import (
    V1ObjectMeta,
    V1PodSpec, 
    V1Container, 
    V1Pod, 
    V1EnvVar, 
    V1Volume, 
    V1VolumeMount, 
    V1EmptyDirVolumeSource,
)
from requests.auth import HTTPBasicAuth
from sqlalchemy import func
from .config import (
    get_environment_image, 
    get_playground_controller_image,
    get_backend_socketio_endpoint,
    get_jwt_signing_key,
    get_basic_auth_username,
    get_basic_auth_password,
    get_base_api_endpoint,
    get_termination_grace_period,
    get_image_pull_secret
)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load the Kubernetes configuration
config.load_incluster_config()

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

def get_unreserved_sessions():
    session = get_db_session()
    statement = select(PlaygroundSession).where(PlaygroundSession.instance_hostname == None)
    result = session.exec(statement).all()
    session.close()
    return result

def remove_session(session_id: uuid.UUID):
    session = get_db_session()
    statement = select(PlaygroundSession).where(PlaygroundSession.id == session_id)
    result = session.exec(statement).one()
    session.delete(result)
    session.commit()
    session.close()

def assign_session(session_id: uuid.UUID, instance_hostname: str):
    """
    Updates a session with the instance hostname of the pod it is assigned to

    Args:
        session_id (uuid.UUID): The session ID
        instance_hostname (str): The hostname of the pod
    """
    
    db_session = get_db_session()
    statement = select(PlaygroundSession).where(PlaygroundSession.id == session_id)
    result = db_session.exec(statement).one()
    result.instance_hostname = instance_hostname
    db_session.commit()

def unassign_session(session_id: uuid.UUID):
    session = get_db_session()
    statement = select(PlaygroundSession).where(PlaygroundSession.id == session_id)
    result = session.exec(statement).one()
    result.instance_hostname = None
    session.add(result)
    session.commit()
    session.close()

def get_reserved_sessions():
    session = get_db_session()
    statement = select(PlaygroundSession).where(PlaygroundSession.instance_hostname != None)
    result = session.exec(statement).all()
    session.close()
    return result

def create_new_pod(session_id: str, instance_type: str):
    """
    Creates a new pod for a playground session

    Args:
        session_id (str): The session ID
        instance_type (str): The flavor of the environment

    Returns:
        str: The name of the created pod
    """
    
    v1 = client.CoreV1Api()
    
    # Define the pod
    pod = V1Pod(
        metadata=V1ObjectMeta(
            name=f"playground-{session_id}",
            labels={
                "app": "playground",
                "playground-session-id": session_id
            }
        ),
        spec=V1PodSpec(
            termination_grace_period_seconds=get_termination_grace_period(),
            containers=[
                V1Container(
                    name="playground-controller", 
                    image=get_playground_controller_image(),
                    volume_mounts=[
                        V1VolumeMount(
                            name="playground-shared",
                            mount_path="/userland"
                        ),
                        V1VolumeMount(
                            name="playground-hidden",
                            mount_path="/playground",
                            read_only=True
                        )
                    ],
                    env=[
                        V1EnvVar(
                            name="BACKEND_SOCKETIO_ENDPOINT",
                            value=get_backend_socketio_endpoint()
                        ),
                        V1EnvVar(
                            name="JWT_SIGNING_KEY",
                            value=get_jwt_signing_key()
                        ),
                        V1EnvVar(
                            name="SESSION_ID",
                            value=session_id
                        )
                    ]
                ),
                V1Container(
                    name=f"{instance_type}-environment",
                    image=get_environment_image(instance_type),
                    volume_mounts=[
                        V1VolumeMount(
                            name="playground-shared",
                            mount_path="/userland"
                        ),
                        V1VolumeMount(
                            name="playground-hidden",
                            mount_path="/playground"
                        )
                    ]
                )
            ],
            volumes=[
                V1Volume(
                    name="playground-shared",
                    empty_dir=V1EmptyDirVolumeSource()
                ),
                V1Volume(
                    name="playground-hidden",
                    empty_dir=V1EmptyDirVolumeSource()
                )
            ]
        )
    )
    
    image_pull_secret = get_image_pull_secret()
    
    if image_pull_secret:
        pod.spec.image_pull_secrets = [{"name": image_pull_secret}]
    
    # Create the pod
    v1.create_namespaced_pod(namespace="eduvize", body=pod)
    
    logging.info("Created new pod")
    
    return pod.metadata.name

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
    api_base_url = get_base_api_endpoint()
    username = get_basic_auth_username()
    password = get_basic_auth_password()
    url = f"{api_base_url}/playground/internal/session"

    try:
        logging.info(f"Attempting to call cleanup API for pod {pod_name}")
        response = requests.delete(url, json={"hostname": pod_name}, auth=HTTPBasicAuth(username, password))
        response.raise_for_status()
        logging.info(f"Successfully called cleanup API for pod {pod_name}")
    except requests.RequestException as e:
        logging.error(f"Failed to call cleanup API for pod {pod_name}: {e}")
    
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
        try:
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
                
        except Exception as e:
            logging.error(f"An error occurred during the scaling process: {e}")
        
        logging.info(f"Sleeping for {interval_seconds} seconds before next check")
        time.sleep(interval_seconds)