import os
import re
import subprocess
import time
import requests
import hashlib
import shutil
import urllib.request
import tarfile
import docker
import socket


def getUrl(timeout=5) -> str:
    try:
        response = requests.get("https://ident.me", timeout=timeout)
        response.raise_for_status()  # Raises a HTTPError if the response was unsuccessful
        result = response.text
    except requests.exceptions.RequestException as x:
        print(type(x), x)
        result = "0.0.0.0"
    return result


class findora_env:
    toolbox_version = "1.3.1"
    server_host_name = socket.gethostname()
    user_home_dir = os.path.expanduser("~")
    dotenv_file = f"{user_home_dir}/.findora.env"
    active_user_name = os.path.split(user_home_dir)[-1]
    findora_root = "/data/findora"
    findora_root_mainnet = f"{findora_root}/mainnet"
    findora_root_testnet = f"{findora_root}/testnet"
    toolbox_location = os.path.join(user_home_dir, "findora-toolbox")
    staker_memo_path = os.path.join(user_home_dir, "staker_memo")
    our_external_ip = getUrl()
    findora_menu = os.path.join(toolbox_location, "src", "messages", "framenu.txt")
    container_name = "findorad"
    migrate_dir = os.path.join(user_home_dir, "migrate")
    fra_env = "prod"
    findora_backup = os.path.join(user_home_dir, "findora_backup")


def execute_command(command):
    subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)


def ask_yes_no(question: str) -> bool:
    yes_no_answer = ""
    while not yes_no_answer.startswith(("Y", "N")):
        yes_no_answer = input(f"{question}: ").upper()
    if yes_no_answer.startswith("Y"):
        return True
    return False


def compare_two_files(input1, input2) -> None:
    # open the files
    file1 = open(input1, "rb")
    file2 = open(input2, "rb")

    # generate their hashes
    hash1 = hashlib.md5(file1.read()).hexdigest()
    hash2 = hashlib.md5(file2.read()).hexdigest()

    # compare the hashes
    if hash1 == hash2:
        return True
    else:
        return False


def get_file_size(url):
    response = requests.head(url)
    file_size = int(response.headers.get("Content-Length", 0))
    return file_size


def get_available_space(directory):
    """Get the available disk space in bytes at the given directory."""
    stat = os.statvfs(directory)
    return stat.f_bavail * stat.f_frsize


def get_live_version(server_url):
    # Make a GET request to the URL
    response = requests.get(f"{server_url}:8668/version")

    # Check if the request was successful
    if response.status_code == 200:
        # Extract the version using a regular expression
        match = re.search(r"v[\d\.]+-release", response.text)
        if match:
            LIVE_VERSION = match.group()
            return LIVE_VERSION
    else:
        print(
            f"Failed to retrieve the version from Findora's server, please try again later. HTTP Response Code: {response.status_code}"
        )
        exit(1)


def format_duration(seconds):
    if seconds < 0:
        seconds = 0
    """Convert duration in seconds to hms format."""
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    return f"{int(hours)}h {int(minutes)}m {int(seconds)}s"


def download_progress_hook(count, block_size, total_size):
    global start_time
    if count == 0:
        start_time = time.time()
        return
    duration = time.time() - start_time
    progress_size = int(count * block_size)
    speed = progress_size / duration
    percent = int(count * block_size * 100 / total_size)
    time_remaining = ((total_size - progress_size) / speed) if speed > 0 else 0
    formatted_progress_size = format_size(progress_size)
    formatted_total_size = format_size(total_size)
    formatted_speed = format_size(speed, is_speed=True)
    formatted_duration = format_duration(duration)
    formatted_time_remaining = format_duration(time_remaining)
    print(
        f"Downloaded {formatted_progress_size} of {formatted_total_size} ({percent}%). "
        f"Speed: {formatted_speed}. Elapsed Time: {formatted_duration}. Time remaining: {formatted_time_remaining}.                    ",
        end="\r",
    )


def install_fn_app():
    subprocess.run(
        ["wget", "https://github.com/FindoraNetwork/findora-wiki-docs/raw/main/.gitbook/assets/fn"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=True,
    )
    subprocess.run(["chmod", "+x", "fn"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    subprocess.run(["sudo", "mv", "fn", "/usr/local/bin/"], check=True)
    print("* fn app installed.")


def local_server_setup(keypath, ROOT_DIR, USERNAME, server_url, network, FINDORAD_IMG):
    # Extract node_mnemonic from keypath file
    with open(keypath, "r") as file:
        content = file.read()
        node_mnemonic = re.search(r"Mnemonic:[^ ]* (.*)", content).group(1)

    # Write node_mnemonic to node.mnemonic file
    node_mnemonic_path = os.path.join(ROOT_DIR, "node.mnemonic")
    with open(node_mnemonic_path, "w") as file:
        file.write(node_mnemonic)

    # Copy node.mnemonic to backup directory
    shutil.copy(node_mnemonic_path, f"/home/{USERNAME}/findora_backup/node.mnemonic")
    print(f"* Setup {node_mnemonic_path}, copied to ~/findora_backup/node.mnemonic")

    # Run FN setup commands
    execute_command(["fn", "setup", "-S", server_url])
    execute_command(["fn", "setup", "-K", os.path.join(ROOT_DIR, "tendermint/config/priv_validator_key.json")])
    execute_command(["fn", "setup", "-O", node_mnemonic_path])
    print("* fn application has been configured.")

    # Clean old data and config files
    network_dir = os.path.join(ROOT_DIR, network)
    shutil.rmtree(network_dir, ignore_errors=True)
    os.makedirs(network_dir)

    try:
        # Create a Docker client
        client = docker.from_env()

        # Define the volume mapping
        volumes = {
            os.path.join(ROOT_DIR, "tendermint"): {
                "bind": "/root/.tendermint",
                "mode": "rw",
            }
        }

        # Run the Docker container in blocking mode to await finish
        client.containers.run(
            image=FINDORAD_IMG,
            command=["init", f"--{network}"],
            volumes=volumes,
            remove=True,  # Equivalent to --rm
        )

    except docker.errors.APIError as e:
        print(f"* Docker API error: {e}")
    finally:
        # Close the Docker client
        try:
            client.close()
        except UnboundLocalError:
            pass  # client was not successfully initialized

    # Reset permissions on tendermint folder after init
    chown_dir(os.path.join(ROOT_DIR, "tendermint"), USERNAME, USERNAME)

    # Backup new priv_validator_key.json
    if os.path.exists(f"/home/{USERNAME}/findora_backup/config"):
        shutil.rmtree(f"/home/{USERNAME}/findora_backup/config")
    shutil.copytree(os.path.join(ROOT_DIR, "tendermint/config"), f"/home/{USERNAME}/findora_backup/config")
    print(f"* Copied new priv_validator_key.json to ~/findora_backup/config")


def load_server_data(ENV, network, ROOT_DIR, region):
    # Download latest link and get url
    if region == "na" or network == "testnet":
        latest_url = f"https://{ENV}-{network}-us-west-2-chain-data-backup.s3.us-west-2.amazonaws.com/latest"
    elif region == "eu" and network == "mainnet":
        latest_url = f"https://{ENV}-{network}-eu-download.s3.eu-central-1.amazonaws.com/latest"
    latest_file = os.path.join(ROOT_DIR, "latest")
    urllib.request.urlretrieve(latest_url, latest_file)

    with open(latest_file, "r") as file:
        CHAINDATA_URL, CHECKSUM_LATEST = file.read().strip().split(",")

    # Remove old data
    shutil.rmtree(os.path.join(ROOT_DIR, "findorad"), ignore_errors=True)
    shutil.rmtree(os.path.join(ROOT_DIR, "tendermint", "data"), ignore_errors=True)
    shutil.rmtree(os.path.join(ROOT_DIR, "tendermint", "config", "addrbook.json"), ignore_errors=True)

    # Get the size of snapshot first
    snapshot_size = get_file_size(CHAINDATA_URL)
    initial_required_size = snapshot_size * 3.5
    available_space = get_available_space(ROOT_DIR)

    if available_space < (initial_required_size):
        print(
            f"Error: Not enough disk space available. Minimum Required: {format_size(initial_required_size)}+, Available: {format_size(available_space)}."
        )
        question = ask_yes_no("Would you like to continue anyway (at own risk of running out of storage)? (y/n): ")
        if not question:
            exit(1)
    else:
        print(
            f"* Available disk space: {format_size(available_space)} - Estimated required space: {format_size(initial_required_size)}"
        )

    # Check snapshot file md5sum
    snapshot_file = os.path.join(ROOT_DIR, "snapshot")
    while True:
        print("Downloading snapshot...")
        urllib.request.urlretrieve(CHAINDATA_URL, snapshot_file, reporthook=download_progress_hook)
        print("\nDownload complete, calculating checksum now...")

        # Calculate the md5 checksum of the downloaded file
        md5_hash = hashlib.md5()
        with open(snapshot_file, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                md5_hash.update(byte_block)
        CHECKSUM = md5_hash.hexdigest()

        if CHECKSUM_LATEST and CHECKSUM_LATEST == CHECKSUM:
            print("Checksum matches, extracting snapshot now...")
            break
        else:
            print("Checksum does not match.")
            retry = ask_yes_no("Checksum verification failed. Would you like to try downloading again? (y/n): ")
            if not retry:
                print("Exiting due to checksum verification failure.")
                exit(1)

    # Define the directory paths
    SNAPSHOT_DIR = os.path.join(ROOT_DIR, "snapshot_data")
    LEDGER_DIR = os.path.join(ROOT_DIR, "findorad")
    TENDERMINT_DIR = os.path.join(ROOT_DIR, "tendermint", "data")

    # Create the snapshot directory
    os.makedirs(SNAPSHOT_DIR, exist_ok=True)

    # Check available disk space
    required_space = snapshot_size * 2.5
    available_space = get_available_space(SNAPSHOT_DIR)
    if available_space < required_space:
        print(
            f"Error: Not enough disk space available. Minimum Required: {format_size(required_space)}+, Available: {format_size(available_space)}."
        )
        question = ask_yes_no("Would you like to continue anyway (at own risk of running out of storage)? (y/n): ")
        if not question:
            exit(1)
    else:
        print(
            f"* Available disk space: {format_size(available_space)} - Estimated required space: {format_size(required_space)} - Estimated available space after unpacking: {format_size(available_space - required_space - snapshot_size)} "
        )

    # Extract the tar archive and check the exit status
    print("Extracting snapshot and setting up the local node...")
    try:
        with tarfile.open(snapshot_file, "r:gz") as tar:
            extracted_count = 0
            for member in tar:
                tar.extract(member, path=SNAPSHOT_DIR)
                extracted_count += 1
                print(f"Extracted {extracted_count} files...", end="\r")
        print("\nSnapshot extraction completed.")
    except OSError as e:
        if e.errno == 28:  # No space left on device
            print("Error: Extraction failed due to insufficient disk space.")
        else:
            print(f"Error: Extraction failed with error: {e}")
        exit(1)

    # Move the extracted files to the desired locations
    shutil.move(os.path.join(SNAPSHOT_DIR, "data", "ledger"), LEDGER_DIR)
    shutil.move(os.path.join(SNAPSHOT_DIR, "data", "tendermint", "mainnet", "node0", "data"), TENDERMINT_DIR)

    # Remove the temporary directories and files
    shutil.rmtree(SNAPSHOT_DIR)
    os.remove(snapshot_file)

    print(
        f"* Snapshot extracted and download removed, current disk space free space: {format_size(get_available_space(ROOT_DIR))}"
    )


def start_local_validator(
    ROOT_DIR, FINDORAD_IMG, local_node_status, network, CONTAINER_NAME, ENDPOINT_STATUS_URL, RETRY_INTERVAL
):
    # Create a Docker client
    client = docker.from_env()

    try:
        # Check if a container with the same name already exists and remove it if it does
        stop_and_remove_container(CONTAINER_NAME)

        # Set the command string based on the network
        command_suffix = "--ledger-dir /tmp/findora --tendermint-host 0.0.0.0 --tendermint-node-key-config-path='/root/.tendermint/config/priv_validator_key.json' --enable-query-service"
        command = f"node {command_suffix}"
        if network == "testnet":
            command = f"node --checkpoint-file=/root/checkpoint.toml {command_suffix}"

        # Set the chain_id based on the network
        chain_id = "2153" if network == "testnet" else "2152"

        # Define the base volumes
        volumes = {
            f"{ROOT_DIR}/tendermint": {"bind": "/root/.tendermint", "mode": "rw"},
            f"{ROOT_DIR}/findorad": {"bind": "/tmp/findora", "mode": "rw"},
        }

        # Add additional volume for testnet
        if network == "testnet":
            volumes[f"{ROOT_DIR}/checkpoint.toml"] = {"bind": "/root/checkpoint.toml", "mode": "rw"}

        # Create the container
        print(f"* Starting {CONTAINER_NAME} container on {network} chain id {chain_id} now...")

        container = client.containers.run(
            image=FINDORAD_IMG,
            name=CONTAINER_NAME,
            detach=True,
            volumes=volumes,
            ports={
                "8669/tcp": 8669,
                "8668/tcp": 8668,
                "8667/tcp": 8667,
                "8545/tcp": 8545,
                "26657/tcp": 26657,
            },
            environment={"EVM_CHAIN_ID": chain_id},
            command=command,
        )

        # Pause for container to initialize
        time.sleep(3)

        # Wait for the container to be up and the endpoint to respond
        while True:
            container = client.containers.get(CONTAINER_NAME)
            if container.status == "running":
                print(f"* {CONTAINER_NAME} is running.")
                try:
                    response = requests.get(ENDPOINT_STATUS_URL)
                    if response.ok:
                        print("* Container is up and endpoint is responding.")
                        break
                    else:
                        print("* Container is up, but endpoint is not responding yet. Retrying in 10 seconds...")
                        time.sleep(RETRY_INTERVAL)
                except requests.ConnectionError:
                    print("* Container is up, but endpoint is not responding yet. Retrying in 10 seconds...")
                    time.sleep(RETRY_INTERVAL)
            else:
                print("* Container is not running. Exiting...")
                exit(1)

    except docker.errors.APIError as e:
        print(f"* Docker API error: {e}")
        exit(1)
    finally:
        # Close the Docker client
        client.close()

    # Post Install Stats Report
    print(requests.get(ENDPOINT_STATUS_URL).text)
    print(requests.get("http://localhost:8669/version").text)
    print(requests.get("http://localhost:8668/version").text)
    print(requests.get("http://localhost:8667/version").text)

    if local_node_status == "installer":
        print(
            "Local node initialized! You can now run the migration process or wait for sync and create your validator."
        )
    else:
        print("Local container was updated and restarted!")


def local_key_setup(keypath, ROOT_DIR, network):
    if not os.path.isfile(keypath):
        if os.path.isfile(f"{findora_env.user_home_dir}/findora_backup/tmp.gen.keypair"):
            subprocess.run(
                ["cp", f"{findora_env.user_home_dir}/findora_backup/tmp.gen.keypair", f"{ROOT_DIR}/{network}_node.key"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=True,
            )
            print(f"* tmp.gen.keypair file detected, copying to {network}_node.key")
        elif os.path.isfile(f"{findora_env.user_home_dir}/tmp.gen.keypair"):
            subprocess.run(
                ["cp", f"{findora_env.user_home_dir}/tmp.gen.keypair", f"{ROOT_DIR}/{network}_node.key"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=True,
            )
            print(f"* tmp.gen.keypair file detected, copying to {network}_node.key")
        else:
            with open(f"{ROOT_DIR}/{network}_node.key", "w") as file:
                subprocess.run(["fn", "genkey"], stdout=file, text=True)
            shutil.copyfile(
                f"{ROOT_DIR}/{network}_node.key", f"{findora_env.user_home_dir}/findora_backup/tmp.gen.keypair"
            )
            print(
                f"* No tmp.gen.keypair file detected, generated file, created {network}_node.key and copied to ~/findora_backup/tmp.gen.keypair"
            )


def stop_and_remove_container(container_name):
    # Create a Docker client
    client = docker.from_env()

    try:
        # Try to get the container by name
        container = client.containers.get(container_name)
        print(f"* {container_name} container found, stopping & removing container...")

        # Stop and remove the container
        container.stop()
        container.remove()

    except docker.errors.NotFound:
        print(f"* {container_name} container removed.")
    except docker.errors.APIError as e:
        print(f"* Docker API error: {e}")
        exit(1)
    finally:
        # Close the Docker client
        client.close()

    # Remove the specified file
    file_path = "/data/findora/mainnet/tendermint/config/addrbook.json"
    if os.path.exists(file_path):
        os.remove(file_path)
        print(f"* Removed file: {file_path}")


def create_directory_with_permissions(path, username):
    subprocess.run(["sudo", "mkdir", "-p", path], check=True)
    subprocess.run(
        ["sudo", "chown", "-R", f"{username}:{username}", path],
        check=True,
    )


def format_size(size_in_bytes, is_speed=False):
    """Converts a size in bytes to a human-readable string."""
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size_in_bytes < 1024:
            return f"{size_in_bytes:.2f} {unit}" + ("/s" if is_speed else "")
        size_in_bytes /= 1024
    return f"{size_in_bytes:.2f} PB" + ("/s" if is_speed else "")


def chown_dir(chown_dir, user, group) -> None:
    try:
        subprocess.run(["sudo", "chown", "-R", f"{user}:{group}", chown_dir], check=True)
    except subprocess.CalledProcessError as e:
        # Output a custom error message along with the stderr of the command
        print(f"Failed to change ownership of {chown_dir} to {user}:{group}. Error: {e.stderr.decode()}")
