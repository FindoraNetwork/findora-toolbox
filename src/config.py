import os, socket, requests

def getUrl(timeout=5) -> str:
    try:
        response = requests.get("https://ident.me", timeout=timeout)
        response.raise_for_status()  # Raises a HTTPError if the response was unsuccessful
        result = response.text
    except requests.exceptions.RequestException as x:
        print(type(x), x)
        result = '0.0.0.0'
    return result

class findora_env:
    toolbox_version = '1.1.7'
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
