import os
import re
import subprocess
import time
import requests
import hashlib
import shutil
import urllib.request
import tarfile
from config import findora_env
from shared import stop_and_remove_container


def check_env(keypath, network, FN, USERNAME):
    for tool in ["wget", "curl", "pv", "docker"]:
        if subprocess.call(["which", tool], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) != 0:
            print(
                f"* \033[31;01m{tool}\033[00m has not been installed and made available to {USERNAME}!\n"
                + f"* Run the following setup commands and try again:\n\n"
                + 'apt-get update && apt-get upgrade -y && curl -fsSL https://download.docker.com/linux/ubuntu/gpg | apt-key add - && add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu focal stable" && apt install apt-transport-https ca-certificates curl pv software-properties-common docker-ce docker-ce-cli dnsutils docker-compose containerd.io bind9-dnsutils git python3-pip python3-dotenv unzip -y && systemctl start docker && systemctl enable docker && usermod -aG docker servicefindora'
            )
            subprocess.run(["rm", f"{findora_env.user_home_dir}/.findora.env"], check=True)
            exit(1)

    if not os.path.isfile(keypath):
        print(f"* No tmp.gen.keypair file detected, generating file and creating to {network}_node.key")
        with open("/tmp/tmp.gen.keypair", "w") as file:
            subprocess.run([FN, "genkey"], stdout=file, text=True)


def set_binaries(FINDORAD_IMG, ROOT_DIR):
    if (
        subprocess.run(
            ["docker", "pull", FINDORAD_IMG], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        ).returncode
        != 0
    ):
        print("Failed to pull Docker image.")
        exit(1)

    if (
        subprocess.run(
            [
                "wget",
                "-T",
                "10",
                "https://github.com/FindoraNetwork/findora-wiki-docs/raw/main/.gitbook/assets/fn",
                "-O",
                "fn",
                "-q",
            ]
        ).returncode
        != 0
    ):
        print("Failed to download fn.")
        exit(1)

    new_path = f"{ROOT_DIR}/bin"
    subprocess.run(["rm", "-rf", new_path], stderr=subprocess.DEVNULL)
    subprocess.run(["mkdir", "-p", new_path], check=True)
    subprocess.run(["mv", "fn", new_path], check=True)
    subprocess.run(["chmod", "-R", "+x", new_path], check=True)


def install_fn_app():
    # Install fn App
    subprocess.run(
        ["wget", "https://github.com/FindoraNetwork/findora-wiki-docs/raw/main/.gitbook/assets/fn"], check=True
    )
    subprocess.run(["chmod", "+x", "fn"], check=True)
    subprocess.run(["sudo", "mv", "fn", "/usr/local/bin/"], check=True)


def config_local_node(keypath, ROOT_DIR, USERNAME, SERV_URL, network, FINDORAD_IMG, CONTAINER_NAME, FN):
    # Extract node_mnemonic and xfr_pubkey from keypath file
    with open(keypath, "r") as file:
        content = file.read()
        node_mnemonic = re.search(r"Mnemonic:[^ ]* (.*)", content).group(1)
        xfr_pubkey = re.search(r'pub_key: *"([^"]*)', content).group(1)

    # Write node_mnemonic to node.mnemonic file
    with open(f"{ROOT_DIR}/node.mnemonic", "w") as file:
        file.write(node_mnemonic)

    # Copy node.mnemonic to backup directory
    subprocess.run(["cp", f"{ROOT_DIR}/node.mnemonic", f"/home/{USERNAME}/findora_backup/node.mnemonic"], check=True)

    # Run FN setup commands
    subprocess.run([FN, "setup", "-S", SERV_URL], check=True)
    subprocess.run([FN, "setup", "-K", f"{ROOT_DIR}/tendermint/config/priv_validator_key.json"], check=True)
    subprocess.run([FN, "setup", "-O", f"{ROOT_DIR}/node.mnemonic"], check=True)

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
    stop_and_remove_container("findorad")


def get_snapshot(ENV, network, ROOT_DIR, region):
    # Download latest link and get url
    if region == "na":
        latest_url = f"https://{ENV}-{network}-us-west-2-chain-data-backup.s3.us-west-2.amazonaws.com/latest"
    elif region == "eu":
        latest_url = f"https://${ENV}-${network}-eu-download.s3.eu-central-1.amazonaws.com/latest"
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
        urllib.request.urlretrieve(CHAINDATA_URL, snapshot_file)

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
        tar.extractall(path=SNAPSHOT_DIR)

    # Move the extracted files to the desired locations
    shutil.move(os.path.join(SNAPSHOT_DIR, "data", "ledger"), LEDGER_DIR)
    shutil.move(os.path.join(SNAPSHOT_DIR, "data", "tendermint", "mainnet", "node0", "data"), TENDERMINT_DIR)

    # Remove the temporary directories and files
    shutil.rmtree(SNAPSHOT_DIR)
    os.remove(snapshot_file)


def create_local_node(ROOT_DIR):
    # Define the Docker image and container name
    FINDORAD_IMG = "findoranetwork/findorad:latest"  # Replace with the actual image tag
    CONTAINER_NAME = "findorad"

    # Run the Docker container
    subprocess.run(
        [
            "docker",
            "run",
            "-d",
            "-v",
            f"{ROOT_DIR}/tendermint:/root/.tendermint",
            "-v",
            f"{ROOT_DIR}/findorad:/tmp/findora",
            "-p",
            "8669:8669",
            "-p",
            "8668:8668",
            "-p",
            "8667:8667",
            "-p",
            "8545:8545",
            "-p",
            "26657:26657",
            "-e",
            "EVM_CHAIN_ID=2152",
            "--name",
            CONTAINER_NAME,
            FINDORAD_IMG,
            "node",
            "--ledger-dir",
            "/tmp/findora",
            "--tendermint-host",
            "0.0.0.0",
            "--tendermint-node-key-config-path",
            "/root/.tendermint/config/priv_validator_key.json",
            "--enable-query-service",
        ]
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

    # Post Install Stats Report
    print(requests.get("http://localhost:26657/status").text)
    print(requests.get("http://localhost:8669/version").text)
    print(requests.get("http://localhost:8668/version").text)
    print(requests.get("http://localhost:8667/version").text)

    print("Local node initialized! You can now run the migration process or wait for sync and create your validator.")


def run_full_installer(network, region):
    USERNAME = findora_env.active_user_name
    if network == "mainnet":
        ENV = "prod"
    elif network == "testnet":
        ENV = "test"
    SERV_URL = f"https://{ENV}-{network}.{ENV}.findora.org"
    LIVE_VERSION = subprocess.getoutput(f"curl -s {SERV_URL}:8668/version | awk -F\\  '{{print $2}}'")
    FINDORAD_IMG = f"findoranetwork/findorad:{LIVE_VERSION}"
    ROOT_DIR = f"/data/findora/{network}"
    keypath = f"{ROOT_DIR}/{network}_node.key"
    FN = f"{ROOT_DIR}/bin/fn"
    CONTAINER_NAME = "findorad"

    install_fn_app()

    # Make Directories & Set Permissions
    subprocess.run(["sudo", "mkdir", "-p", "/data/findora"], check=True)
    subprocess.run(["mkdir", "-p", f"/home/{USERNAME}/findora_backup"], check=True)
    subprocess.run(["sudo", "chown", "-R", f"{USERNAME}:{USERNAME}", "/data/findora/"], check=True)
    subprocess.run(["mkdir", "-p", f"/data/findora/{network}"], check=True)

    # Check for existing files
    check_env(keypath, network, FN, USERNAME)

    subprocess.run(["cp", "/tmp/tmp.gen.keypair", f"/home/{USERNAME}/findora_backup/tmp.gen.keypair"], check=True)
    subprocess.run(["mv", "/tmp/tmp.gen.keypair", f"/data/findora/{network}/{network}_node.key"], check=True)

    uname = subprocess.getoutput("uname -s")
    if uname == "Linux":
        set_binaries(FINDORAD_IMG, ROOT_DIR)
    elif uname == "Darwin":
        set_binaries(FINDORAD_IMG, ROOT_DIR)
    else:
        print("Unsupported system platform!")
        exit(1)

    # Config local node
    config_local_node(keypath, ROOT_DIR, USERNAME, SERV_URL, network, FINDORAD_IMG, CONTAINER_NAME, FN)

    # get snapshot
    get_snapshot(ENV, network, ROOT_DIR, region)

    # get checkpoint on testnet
    if network == "testnet":
        subprocess.run(["sudo", "rm", "-rf", f"{ROOT_DIR}/checkpoint.toml"], check=True)
        subprocess.run(["wget", "-O", f"{ROOT_DIR}/checkpoint.toml"], check=True)

    # Start findorad
    create_local_node(ROOT_DIR)
