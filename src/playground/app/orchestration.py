import os
from kubernetes import client as k8s_client, config as k8s_config

def mark_for_deletion():
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
    
    v1.patch_namespaced_pod(
        name=hostname, 
        namespace=namespace, 
        body=patch_body
    )
    
    print(f"Pod {hostname} was marked for removal")