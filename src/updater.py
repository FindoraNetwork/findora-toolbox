import os
import subprocess
from shared import chown_dir, start_local_validator, stop_and_remove_container, get_live_version
from config import config


def run_update_restart(network=os.environ.get("FRA_NETWORK")):
    USERNAME = config.active_user_name
    ENV = "prod"
    server_url = f"https://{ENV}-{network}.{ENV}.findora.org"
    LIVE_VERSION = get_live_version(server_url)
    FINDORAD_IMG = f"findoranetwork/findorad:v{LIVE_VERSION}"
    ROOT_DIR = f"/data/findora/{network}"
    CONTAINER_NAME = "findorad"
    ENDPOINT_STATUS_URL = "http://localhost:26657/status"
    RETRY_INTERVAL = 10

    chown_dir(ROOT_DIR, USERNAME, USERNAME)

    stop_and_remove_container(CONTAINER_NAME)

    # get checkpoint on testnet
    if network == "testnet":
        CHECKPOINT_URL = (
            f"https://{ENV}-{network}-us-west-2-ec2-instance.s3.us-west-2.amazonaws.com/{network}/checkpoint"
        )
        subprocess.run(
            ["sudo", "rm", "-rf", f"{ROOT_DIR}/checkpoint.toml"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True,
        )
        subprocess.run(
            ["wget", "-O", f"{ROOT_DIR}/checkpoint.toml", f"{CHECKPOINT_URL}"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True,
        )

    # Start findorad
    start_local_validator(
        ROOT_DIR, FINDORAD_IMG, "updater", network, CONTAINER_NAME, ENDPOINT_STATUS_URL, RETRY_INTERVAL
    )
