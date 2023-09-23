import docker, re, os, subprocess


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


def create_directory_with_permissions(path, username):
    subprocess.run(["sudo", "mkdir", "-p", path], check=True)
    subprocess.run(["sudo", "chown", "-R", f"{username}:{username}", path], check=True)


def format_size(size_in_bytes, is_speed=False):
    """Converts a size in bytes to a human-readable string."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_in_bytes < 1024:
            return f"{size_in_bytes:.2f} {unit}" + ("/s" if is_speed else "")
        size_in_bytes /= 1024
    return f"{size_in_bytes:.2f} PB" + ("/s" if is_speed else "")