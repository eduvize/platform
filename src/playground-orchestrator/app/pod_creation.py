import logging
from kubernetes import client, config
from kubernetes.client import (
    V1ObjectMeta,
    V1PodSpec, 
    V1Container, 
    V1Pod, 
    V1EnvVar,
    V1SecurityContext,
    V1EnvVarSource,
    V1SecretKeySelector
)
from .config import (
    get_termination_grace_period,
    get_image_pull_secret,
    get_playground_host_image,
    get_jwt_signing_key,
    get_backend_api_endpoint,
    get_backend_socketio_endpoint
)

def build_secret_var(env_name: str, secret: str, key: str):
    return V1EnvVar(
        name=env_name,
        value_from=V1EnvVarSource(
            secret_key_ref=V1SecretKeySelector(
                name=secret,
                key=key
            )
        )
    )

def create_new_pod(session_id: str, image_tag: str, environment_id: str):
    """
    Creates a new pod for a playground session

    Args:
        session_id (str): The session ID
        image_tag (str): The image tag for the environment
        environment_id (str): The environment ID

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
                    name=f"host",
                    image=get_playground_host_image(),
                    security_context=V1SecurityContext(
                        privileged=True
                    ),
                    env=[
                        build_secret_var("REGISTRY", "playground-image-registry", "host"),
                        build_secret_var("REGISTRY_USER", "playground-image-registry", "user"),
                        build_secret_var("REGISTRY_CRED", "playground-image-registry", "password"),
                        V1EnvVar(
                            name="SESSION_ID",
                            value=session_id
                        ),
                        V1EnvVar(
                            name="IMAGE_TAG",
                            value=image_tag  
                        ),
                        V1EnvVar(
                            name="ENVIRONMENT_ID",
                            value=environment_id  
                        ),
                        V1EnvVar(
                            name="JWT_SIGNING_KEY",
                            value=get_jwt_signing_key()
                        ),
                        V1EnvVar(
                            name="BACKEND_API_ENDPOINT",
                            value=get_backend_api_endpoint()
                        ),
                        V1EnvVar(
                            name="BACKEND_SOCKETIO_ENDPOINT",
                            value=get_backend_socketio_endpoint()
                        ),
                        V1EnvVar(
                            name="DOCKER_HOST",
                            value="unix:///var/run/docker.sock"
                        )
                    ]
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