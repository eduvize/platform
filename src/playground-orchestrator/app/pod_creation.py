import logging
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
from .config import (
    get_environment_image, 
    get_playground_controller_image,
    get_backend_socketio_endpoint,
    get_jwt_signing_key,
    get_termination_grace_period,
    get_image_pull_secret
)

def create_new_pod(session_id: str, instance_type: str):
    """
    Creates a new pod for a playground session

    Args:
        session_id (str): The session ID
        instance_type (str): The flavor of the environment

    Returns:
        str: The name of the created pod
    """

    config.load_incluster_config()    
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