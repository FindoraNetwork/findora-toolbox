import docker, re, os

def stop_and_remove_container(container_name):
    # Create a Docker client
    client = docker.from_env()

    # List all containers
    containers = client.containers.list(all=True)

    # Check if the container with the specified name is running
    container_found = any(re.fullmatch(container_name, container.name) for container in containers)

    if container_found:
        print(f"{container_name} Container found, stopping container to restart.")

        # Stop and remove the container
        container = client.containers.get(container_name)
        container.stop()
        container.remove()

        # Remove the specified file
        file_path = "/data/findora/mainnet/tendermint/config/addrbook.json"
        if os.path.exists(file_path):
            os.remove(file_path)
    else:
        print(f"{container_name} container stopped or does not exist, continuing.")