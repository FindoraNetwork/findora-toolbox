import subprocess
import os
from config import findora_env
from shared import (
    stop_and_remove_container,
    chown_dir,
    get_live_version,
    create_local_node,
    get_snapshot,
)


def run_safety_clean(network = os.environ.get("FRA_NETWORK"), region = os.environ.get("FRA_REGION")):
    USERNAME = findora_env.active_user_name
    ENV = "prod"
    server_url = f"https://{ENV}-{network}.{ENV}.findora.org"
    LIVE_VERSION = get_live_version(server_url)
    FINDORAD_IMG = f"findoranetwork/findorad:{LIVE_VERSION}"
    ROOT_DIR = f"/data/findora/{network}"
    CONTAINER_NAME = "findorad"
    ENDPOINT_STATUS_URL = "http://localhost:26657/status"
    RETRY_INTERVAL = 10

    chown_dir(ROOT_DIR, USERNAME, USERNAME)

    stop_and_remove_container(CONTAINER_NAME)

    # get snapshot
    get_snapshot(ENV, network, ROOT_DIR, region)

    # get checkpoint on testnet
    if network == "testnet":
        CHECKPOINT_URL = f"https://{ENV}-{network}-us-west-2-ec2-instance.s3.us-west-2.amazonaws.com/{network}/checkpoint"
        subprocess.run(["sudo", "rm", "-rf", f"{ROOT_DIR}/checkpoint.toml"], check=True)
        subprocess.run(["wget", "-O", f"{ROOT_DIR}/checkpoint.toml", f"{CHECKPOINT_URL}"], check=True)

    # Start findorad
    create_local_node(ROOT_DIR, FINDORAD_IMG, "safety_clean", network, CONTAINER_NAME, ENDPOINT_STATUS_URL, RETRY_INTERVAL)
