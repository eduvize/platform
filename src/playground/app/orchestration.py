import logging
import os
import requests
import base64
from typing import Optional
from kubernetes import client as k8s_client, config as k8s_config
from .config import get_api_base_url, get_basic_auth_password, get_basic_auth_username, get_session_id_path
from .models import PlaygroundSessionResponse

def create_reservation(hostname: str) -> Optional[PlaygroundSessionResponse]:
    """
    Creates a reservation for a pending session by calling the backend API

    Args:
        hostname (str): The pod hostname of this instance

    Returns:
        str: The session ID of the created reservation, or None if the reservation failed
    """
    
    logging.info(f"Creating reservation for hostname: {hostname}")
    
    basic_auth = base64.b64encode(f"{get_basic_auth_username()}:{get_basic_auth_password()}".encode()).decode()
    
    response = requests.post(
        f"{get_api_base_url()}/playground/internal/reservations",
        headers={
            "Authorization": f"Basic {basic_auth}",
        },
        json={
            "hostname": hostname
        }
    )
    
    logging.info(f"Received response: {response.status_code} - {response.text}")
    
    if response.status_code == 404:
        return None
    
    return PlaygroundSessionResponse.model_validate(response.json())

def validate_reservation(hostname: str) -> bool:
    """
    Checks with the backend API to verify whether or not a session is still valid

    Args:
        hostname (str): The pod hostname of this instance

    Returns:
        bool: True if the session is still valid, False otherwise
    """
    
    basic_auth = base64.b64encode(f"{get_basic_auth_username()}:{get_basic_auth_password()}".encode()).decode()
    
    response = requests.get(
        f"{get_api_base_url()}/playground/internal/reservations/{hostname}",
        headers={
            "Authorization": f"Basic {basic_auth}",
        }
    )
    
    return response.status_code != 404

def set_session_label(session_id: str):
    """
    Sets the session ID as a label on the current pod

    Args:
        session_id (str): The session ID to set as a label
    """
    
    hostname = os.getenv("HOSTNAME")
    namespace = open("/var/run/secrets/kubernetes.io/serviceaccount/namespace", "r").read().strip()
    
    k8s_config.load_incluster_config()
    
    v1 = k8s_client.CoreV1Api()
    
    patch_body = {
        "metadata": {
            "labels": {
                "playground-session-id": session_id
            }
        }
    }
    
    response = v1.patch_namespaced_pod(
        name=hostname, 
        namespace=namespace, 
        body=patch_body
    )
    
    print(f"Pod {hostname} was labeled with session ID {session_id}")

def kill_pod():
    k8s_config.load_incluster_config()
    
    v1 = k8s_client.CoreV1Api()
    
    hostname = os.getenv("HOSTNAME")
    namespace = open("/var/run/secrets/kubernetes.io/serviceaccount/namespace", "r").read().strip()
    
    patch_body = {
        "metadata": {
            "labels": {
                "ready-for-deletion": "true"
            }
        }
    }
    
    response = v1.patch_namespaced_pod(
        name=hostname, 
        namespace=namespace, 
        body=patch_body
    )
    
    print(f"Pod {hostname} was marked for removal")