import requests
import os
import subprocess
import re
from config import findora_env
from shared import chown_dir, create_local_node, stop_and_remove_container, get_live_version


def run_update_restart(network = os.environ.get("FRA_NETWORK")):
    USERNAME = findora_env.active_user_name

    ENV = "prod"

    server_url = f"https://{ENV}-{network}.{ENV}.findora.org"

    LIVE_VERSION = get_live_version(server_url)

    FINDORAD_IMG = f"findoranetwork/findorad:{LIVE_VERSION}"
    CHECKPOINT_URL = f"https://{ENV}-{network}-us-west-2-ec2-instance.s3.us-west-2.amazonaws.com/{network}/checkpoint"
    ROOT_DIR = f"/data/findora/{network}"
    CONTAINER_NAME = "findorad"

    chown_dir(ROOT_DIR, USERNAME, USERNAME)

    stop_and_remove_container(CONTAINER_NAME)

    # get checkpoint on testnet
    if network == "testnet":
        subprocess.run(["sudo", "rm", "-rf", f"{ROOT_DIR}/checkpoint.toml"], check=True)
        subprocess.run(["wget", "-O", f"{ROOT_DIR}/checkpoint.toml", f"{CHECKPOINT_URL}"], check=True)

    # Start findorad
    create_local_node(ROOT_DIR, FINDORAD_IMG, "updater")
