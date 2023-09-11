import os
import yaml
import argparse
from kubernetes import client, config
from kubernetes.client.rest import ApiException

config.load_kube_config()
api = client.CoreV1Api()

def deploy_multi_container_pod(manifest_file_path, node_name):
    try:
        with open(manifest_file_path, 'r') as manifest_file:
            pod_manifest = yaml.safe_load(manifest_file)

        if 'nodeSelector' not in pod_manifest['spec']:
            pod_manifest['spec']['nodeSelector'] = {}
        pod_manifest['spec']['nodeSelector']['kubernetes.io/hostname'] = node_name
        api_response = api.create_namespaced_pod( body=pod_manifest, namespace="default")
        print(f"Pod {api_response.metadata.name} created successfully.")
        
    except ApiException as e:
        raise Exception(f"Error deploying pod: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Handle the automatic deployment of a pod")
    # Options
    parser.add_argument("-f", "--file", help="File path of the pod manifest")
    parser.add_argument("-n", "--node", help="Node name where the pod will be deployed")

    # Parse arguments
    args = parser.parse_args()

    #Check if the arguments are provided
    if not args.file or not args.node:
        parser.print_help()
        exit(1)
    
    # Check if the file exists
    if not os.path.isfile(args.file):
        raise Exception("File ${args.file} not found")

    # Check if the node exists
    try:
        api.read_node(args.node)
    except ApiException as e:
        raise Exception(f"Target node ${args.node} not found")

    deploy_multi_container_pod(args.file, args.node)

