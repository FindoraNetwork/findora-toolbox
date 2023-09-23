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
from colorama import Fore, Back, Style
from config import findora_env
from shared import stop_and_remove_container, create_directory_with_permissions, format_size


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
    print(
        f"Downloaded {formatted_progress_size} of {formatted_total_size} ({percent}%). Speed: {formatted_speed}. Time remaining: {time_remaining:.2f} seconds.",
        end="\r",
    )
    

def install_fn_app():
    subprocess.run(
        ["wget", "https://github.com/FindoraNetwork/findora-wiki-docs/raw/main/.gitbook/assets/fn"], check=True
    )
    subprocess.run(["chmod", "+x", "fn"], check=True)
    subprocess.run(["sudo", "mv", "fn", "/usr/local/bin/"], check=True)


def config_local_node(keypath, ROOT_DIR, USERNAME, SERV_URL, network, FINDORAD_IMG, CONTAINER_NAME):
    # Extract node_mnemonic and xfr_pubkey from keypath file
    with open(keypath, "r") as file:
        content = file.read()
        node_mnemonic = re.search(r"Mnemonic:[^ ]* (.*)", content).group(1)

    # Write node_mnemonic to node.mnemonic file
    with open(f"{ROOT_DIR}/node.mnemonic", "w") as file:
        file.write(node_mnemonic)

    # Copy node.mnemonic to backup directory
    subprocess.run(["cp", f"{ROOT_DIR}/node.mnemonic", f"/home/{USERNAME}/findora_backup/node.mnemonic"], check=True)

    # Run FN setup commands
    subprocess.run(["fn", "setup", "-S", SERV_URL], check=True)
    subprocess.run(["fn", "setup", "-K", f"{ROOT_DIR}/tendermint/config/priv_validator_key.json"], check=True)
    subprocess.run(["fn", "setup", "-O", f"{ROOT_DIR}/node.mnemonic"], check=True)

    # Clean old data and config files
    subprocess.run(["sudo", "rm", "-rf", f"{ROOT_DIR}/{network}"], check=True)
    subprocess.run(["mkdir", "-p", f"{ROOT_DIR}/{network}"], check=True)

    # Tendermint config
    subprocess.run(
        [
            "docker",
            "run",
            "--rm",
            "-v",
            f"{ROOT_DIR}/tendermint:/root/.tendermint",
            FINDORAD_IMG,
            "init",
            f"--{network}",
        ],
        check=True,
    )

    # Reset permissions on tendermint folder after init
    subprocess.run(["sudo", "chown", "-R", f"{USERNAME}:{USERNAME}", f"{ROOT_DIR}/tendermint"], check=True)

    # Backup priv_validator_key.json
    subprocess.run(["cp", "-a", f"{ROOT_DIR}/tendermint/config", f"/home/{USERNAME}/findora_backup/config"], check=True)

    # If you're re-running this for some reason, stop and remove findorad
    print(Fore.MAGENTA)
    stop_and_remove_container("findorad")


def get_snapshot(ENV, network, ROOT_DIR, region):
    # Download latest link and get url
    if region == "na" or network == "testnet":
        latest_url = f"https://{ENV}-{network}-us-west-2-chain-data-backup.s3.us-west-2.amazonaws.com/latest"
    elif region == "eu" and network == "mainnet":
        latest_url = f"https://{ENV}-{network}-eu-download.s3.eu-central-1.amazonaws.com/latest"
    latest_file = os.path.join(ROOT_DIR, "latest")
    urllib.request.urlretrieve(latest_url, latest_file)

    with open(latest_file, "r") as file:
        CHAINDATA_URL, CHECKSUM_LATEST = file.read().strip().split(",")
        print(CHAINDATA_URL)

    # Remove old data
    shutil.rmtree(os.path.join(ROOT_DIR, "findorad"), ignore_errors=True)
    shutil.rmtree(os.path.join(ROOT_DIR, "tendermint", "data"), ignore_errors=True)
    shutil.rmtree(os.path.join(ROOT_DIR, "tendermint", "config", "addrbook.json"), ignore_errors=True)

    # Check snapshot file md5sum
    snapshot_file = os.path.join(ROOT_DIR, "snapshot")
    while True:
        print("Downloading snapshot...")
        urllib.request.urlretrieve(CHAINDATA_URL, snapshot_file, reporthook=download_progress_hook)
        print("\nDownload complete!")

        # Calculate the md5 checksum of the downloaded file
        md5_hash = hashlib.md5()
        with open(snapshot_file, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                md5_hash.update(byte_block)
        CHECKSUM = md5_hash.hexdigest()

        if CHECKSUM_LATEST and CHECKSUM_LATEST == CHECKSUM:
            break

    # Define the directory paths
    SNAPSHOT_DIR = os.path.join(ROOT_DIR, "snapshot_data")
    LEDGER_DIR = os.path.join(ROOT_DIR, "findorad")
    TENDERMINT_DIR = os.path.join(ROOT_DIR, "tendermint", "data")

    # Create the snapshot directory
    os.makedirs(SNAPSHOT_DIR, exist_ok=True)

    # Extract the tar archive and check the exit status
    print("Extracting snapshot and setting up the local node...")
    with tarfile.open(snapshot_file, "r:gz") as tar:
        extracted_count = 0
        for member in tar:
            tar.extract(member, path=SNAPSHOT_DIR)
            extracted_count += 1
            print(f"Extracted {extracted_count} files...", end="\r")
    print("\nExtraction complete!")

    # Move the extracted files to the desired locations
    shutil.move(os.path.join(SNAPSHOT_DIR, "data", "ledger"), LEDGER_DIR)
    shutil.move(os.path.join(SNAPSHOT_DIR, "data", "tendermint", "mainnet", "node0", "data"), TENDERMINT_DIR)

    # Remove the temporary directories and files
    shutil.rmtree(SNAPSHOT_DIR)
    os.remove(snapshot_file)


def create_local_node(ROOT_DIR, FINDORAD_IMG):
    # Define the Docker image and container name
    client = docker.from_env()

    CONTAINER_NAME = "findorad"

    try:
        container = client.containers.run(
            image=FINDORAD_IMG,
            name=CONTAINER_NAME,
            detach=True,
            volumes={
                f"{ROOT_DIR}/tendermint": {"bind": "/root/.tendermint", "mode": "rw"},
                f"{ROOT_DIR}/findorad": {"bind": "/tmp/findora", "mode": "rw"},
            },
            ports={
                "8669/tcp": 8669,
                "8668/tcp": 8668,
                "8667/tcp": 8667,
                "8545/tcp": 8545,
                "26657/tcp": 26657,
            },
            environment={"EVM_CHAIN_ID": "2152"},
            command="node --ledger-dir /tmp/findora --tendermint-host 0.0.0.0 --tendermint-node-key-config-path=/root/.tendermint/config/priv_validator_key.json --enable-query-service",
        )

        # Wait for the container to be up and the endpoint to respond
        while True:
            # Check if the container is running
            result = subprocess.run(["docker", "ps", "--format", "{{.Names}}"], capture_output=True, text=True)
            if CONTAINER_NAME in result.stdout:
                # Check the response from the endpoint
                try:
                    response = requests.get("http://localhost:26657/status")
                    if response.ok:
                        print("Container is up and endpoint is responding.")
                        break
                    else:
                        print("Container is up, but endpoint is not responding yet. Retrying in 10 seconds...")
                        time.sleep(10)
                except requests.ConnectionError:
                    print("Container is up, but endpoint is not responding yet. Retrying in 10 seconds...")
                    time.sleep(10)
            else:
                print("Container is not running. Exiting...")
                exit(1)
    except docker.errors.ContainerError as e:
        print(f"Container error: {e}")
    except docker.errors.ImageNotFound:
        print("Docker image not found.")
    except docker.errors.APIError as e:
        print(f"Docker API error: {e}")

    # Post Install Stats Report
    print(requests.get("http://localhost:26657/status").text)
    print(requests.get("http://localhost:8669/version").text)
    print(requests.get("http://localhost:8668/version").text)
    print(requests.get("http://localhost:8667/version").text)

    print("Local node initialized! You can now run the migration process or wait for sync and create your validator.")


def setup_wallet_key(keypath, ROOT_DIR, network):
    if not os.path.isfile(keypath):
        if os.path.isfile(f"{findora_env.user_home_dir}/findora_backup/tmp.gen.keypair"):
            subprocess.run(["cp", f"{findora_env.user_home_dir}/findora_backup/tmp.gen.keypair", f"{ROOT_DIR}/{network}_node.key"], check=True)
        elif os.path.isfile(f"{findora_env.user_home_dir}/tmp.gen.keypair"):
            subprocess.run(["cp", f"{findora_env.user_home_dir}/tmp.gen.keypair", f"{ROOT_DIR}/{network}_node.key"], check=True)
        else:
            print(f"* No tmp.gen.keypair file detected, generating file and creating to {network}_node.key")
            with open(f"{ROOT_DIR}/{network}_node.key", "w") as file:
                subprocess.run(["fn", "genkey"], stdout=file, text=True)


def run_full_installer(network, region):
    USERNAME = findora_env.active_user_name

    ENV = "prod"

    SERV_URL = f"https://{ENV}-{network}.{ENV}.findora.org"

    # Make a GET request to the URL
    response = requests.get(f"{SERV_URL}:8668/version")

    # Check if the request was successful
    if response.status_code == 200:
        # Extract the version using a regular expression
        match = re.search(r"v[\d\.]+-release", response.text)
        if match:
            LIVE_VERSION = match.group()
    else:
        print(f"Failed to retrieve the version. HTTP Response Code: {response.status_code}")
        exit(1)

    FINDORAD_IMG = f"findoranetwork/findorad:{LIVE_VERSION}"
    CHECKPOINT_URL = f"https://{ENV}-{network}-us-west-2-ec2-instance.s3.us-west-2.amazonaws.com/{network}/checkpoint"
    ROOT_DIR = f"/data/findora/{network}"
    keypath = f"{ROOT_DIR}/{network}_node.key"
    CONTAINER_NAME = "findorad"

    uname = subprocess.getoutput("uname -s")
    if uname == "Linux":
        install_fn_app()
    elif uname == "Darwin":
        # How do we do mac? Same or not sure? Same for now...
        install_fn_app()
    else:
        print("Unsupported system platform!")
        exit(1)

    # Make Directories & Set Permissions
    create_directory_with_permissions("/data/findora", USERNAME)
    subprocess.run(["mkdir", "-p", f"/home/{USERNAME}/findora_backup"], check=True)
    subprocess.run(["mkdir", "-p", ROOT_DIR], check=True)

    # Setup wallet key
    setup_wallet_key(keypath, ROOT_DIR, network)
    
    # Config local node
    config_local_node(keypath, ROOT_DIR, USERNAME, SERV_URL, network, FINDORAD_IMG, CONTAINER_NAME)

    # get snapshot
    get_snapshot(ENV, network, ROOT_DIR, region)

    # get checkpoint on testnet
    if network == "testnet":
        subprocess.run(["sudo", "rm", "-rf", f"{ROOT_DIR}/checkpoint.toml"], check=True)
        subprocess.run(["wget", "-O", f"{ROOT_DIR}/checkpoint.toml", f"{CHECKPOINT_URL}"], check=True)

    # Start findorad
    create_local_node(ROOT_DIR, FINDORAD_IMG)
