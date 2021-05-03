import base64
import json
import os
from types import SimpleNamespace
from urllib.parse import urlparse

import boto3
from kubernetes import client as kubernetes_client, config


def create_or_update_ecr_token_on_k8s_cluster(ecr_gateway):
    ecr_secret_name = os.getenv("ECR_SECRET_NAME", "ecr-token")
    ecr_secret_namespace = os.getenv("ECR_SECRET_NAMESPACE", "cluster-tools")

    ecr_credentials = get_ecr_credentials(ecr_gateway)
    ecr_secret = mount_kubernetes_configjson_secret(ecr_credentials, ecr_secret_name, ecr_secret_namespace)

    try:
        kubernetes_client.CoreV1Api().read_namespaced_secret(ecr_secret_name, ecr_secret_namespace)
        kubernetes_client.CoreV1Api().delete_namespaced_secret(ecr_secret_name, ecr_secret_namespace)
        print("The older secret was removed successfully.")
    except:
        print("The Secret doesn't exist yet or the namespace is incorrect. Ill try to create the secret.")

    kubernetes_client.CoreV1Api().create_namespaced_secret(ecr_secret_namespace, body=ecr_secret)
    print("The secret was created/updated.")


def get_ecr_credentials(ecr_gateway: boto3.client):
    token = ecr_gateway.get_authorization_token()
    user, password = base64.b64decode(token['authorizationData'][0]['authorizationToken'].encode()).decode().split(':')
    registry = urlparse(token['authorizationData'][0]['proxyEndpoint'])

    return SimpleNamespace(user=user, password=password, registry=registry.netloc)


def mount_kubernetes_configjson_secret(docker_credentials, ecr_secret_name, ecr_secret_namespace):
    cred_payload = {
        "auths": {
            docker_credentials.registry: {
                "Username": docker_credentials.user,
                "Password": docker_credentials.password,
            }
        }
    }

    data = {".dockerconfigjson": base64.b64encode(
        json.dumps(cred_payload).encode()
    ).decode()
            }

    return kubernetes_client.V1Secret(
        api_version="v1",
        data=data,
        kind="Secret",
        metadata=dict(name=ecr_secret_name, namespace=ecr_secret_namespace),
        type="kubernetes.io/dockerconfigjson",
    )


if __name__ == '__main__':
    config.load_incluster_config()

    ecr_gateway = boto3.client('ecr')
    create_or_update_ecr_token_on_k8s_cluster(ecr_gateway=ecr_gateway)
