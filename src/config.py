import os, socket, urllib.request
from importlib.metadata import version


def getUrl() -> None:
    try:
        result = urllib.request.urlopen("https://ident.me").read().decode("utf8")
    except Exception as x:
        print(type(x), x)
        result = "0.0.0.0"
    return result


class easy_env_fra:
    easy_version = version('findora_toolbox')
    server_host_name = socket.gethostname()
    user_home_dir = os.path.expanduser("~")
    dotenv_file = f"{user_home_dir}/.easynode.env"
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
