import subprocess
from shared import (
    create_directory_with_permissions,
    install_fn_app,
    local_key_setup,
    local_server_setup,
    load_server_data,
    start_local_validator,
    get_live_version,
    create_staker_memo
)
from config import config

def run_full_installer(network, region):
    USERNAME = config.active_user_name
    # Testnet and mainnet are both prod, can update for mocknet in the future
    ENV = "prod"
    server_url = f"https://{ENV}-{network}.{ENV}.findora.org"
    LIVE_VERSION = get_live_version(server_url)
    if LIVE_VERSION is None:
        print("Failed to get live version from server, exiting...")
        exit(1)
    FRACTAL_IMG = f"fractalfoundation/fractal:v{LIVE_VERSION}"
    ROOT_DIR = f"/data/findora/{network}"
    keypath = f"{ROOT_DIR}/{network}_node.key"
    CONTAINER_NAME = "fractal"
    ENDPOINT_STATUS_URL = "http://localhost:26657/status"
    RETRY_INTERVAL = 10

    uname = subprocess.getoutput("uname -s")
    if uname == "Linux":
        install_fn_app()
    elif uname == "Darwin":
        # How do we do mac? Same or not sure? Same for now...
        install_fn_app()
    else:
        print("Unsupported system platform!")
        exit(1)

    # Staker Memo
    create_staker_memo()

    # Make Directories & Set Permissions
    create_directory_with_permissions("/data/findora", USERNAME)

    # Create backup directory
    subprocess.run(
        ["mkdir", "-p", f"/home/{USERNAME}/findora_backup"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=True,
    )
    subprocess.run(["mkdir", "-p", ROOT_DIR], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

    # Setup wallet key
    local_key_setup(keypath, ROOT_DIR, network)

    # Config local node
    local_server_setup(keypath, ROOT_DIR, USERNAME, server_url, network, FRACTAL_IMG)

    # get snapshot
    load_server_data(ENV, network, ROOT_DIR, region)

    # get checkpoint on testnet
    if network == "testnet":
        CHECKPOINT_URL = (
            f"https://{ENV}-{network}-us-west-2-ec2-instance.s3.us-west-2.amazonaws.com/{network}/checkpoint"
        )
        subprocess.run(
            ["sudo", "rm", "-rf", f"{ROOT_DIR}/checkpoint.toml"],
            check=True,
        )
        subprocess.run(
            ["wget", "-O", f"{ROOT_DIR}/checkpoint.toml", f"{CHECKPOINT_URL}"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True,
        )

    # Start fractal
    start_local_validator(
        ROOT_DIR, FRACTAL_IMG, "installer", network, CONTAINER_NAME, ENDPOINT_STATUS_URL, RETRY_INTERVAL
    )
