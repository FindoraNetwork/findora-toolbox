import re
import subprocess
import requests
from config import findora_env
from shared import create_directory_with_permissions, install_fn_app, setup_wallet_key, config_local_node, get_snapshot, create_local_node, get_live_version


def run_full_installer(network, region):
    USERNAME = findora_env.active_user_name
    ENV = "prod"
    server_url = f"https://{ENV}-{network}.{ENV}.findora.org"

    LIVE_VERSION = get_live_version(server_url)

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
    config_local_node(keypath, ROOT_DIR, USERNAME, server_url, network, FINDORAD_IMG, CONTAINER_NAME)

    # get snapshot
    get_snapshot(ENV, network, ROOT_DIR, region)

    # get checkpoint on testnet
    if network == "testnet":
        subprocess.run(["sudo", "rm", "-rf", f"{ROOT_DIR}/checkpoint.toml"], check=True)
        subprocess.run(["wget", "-O", f"{ROOT_DIR}/checkpoint.toml", f"{CHECKPOINT_URL}"], check=True)

    # Start findorad
    create_local_node(ROOT_DIR, FINDORAD_IMG)
