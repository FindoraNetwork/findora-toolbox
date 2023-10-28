import subprocess
import os
from shared import (
    stop_and_remove_container,
    chown_dir,
    get_live_version,
    start_local_validator,
    load_server_data,
)
from config import config

def run_safety_clean(network=os.environ.get("FRA_NETWORK"), region=os.environ.get("FRA_REGION")):
    USERNAME = config.active_user_name
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
    load_server_data(ENV, network, ROOT_DIR, region)

    # get checkpoint on testnet
    if network == "testnet":
        CHECKPOINT_URL = (
            f"https://{ENV}-{network}-us-west-2-ec2-instance.s3.us-west-2.amazonaws.com/{network}/checkpoint"
        )
        subprocess.run(["sudo", "rm", "-rf", f"{ROOT_DIR}/checkpoint.toml"], check=True)
        subprocess.run(
            ["wget", "-O", f"{ROOT_DIR}/checkpoint.toml", f"{CHECKPOINT_URL}"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True,
        )

    # Start findorad
    start_local_validator(
        ROOT_DIR, FINDORAD_IMG, "safety_clean", network, CONTAINER_NAME, ENDPOINT_STATUS_URL, RETRY_INTERVAL
    )
