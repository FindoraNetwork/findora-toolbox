import os, socket, urllib.request

def getUrl() -> None:
    try:
        result = urllib.request.urlopen("https://ident.me").read().decode("utf8")
    except Exception as x:
        print(type(x),x)
        result = '0.0.0.0'
        pass
    return result

class easy_env_fra:
    easy_version = "1.1.1"
    our_disk_mount = '/data/findora'
    server_host_name = socket.gethostname()
    user_home_dir = os.path.expanduser("~")
    dotenv_file = f"{user_home_dir}/.easynode.env"
    active_user_name = os.path.split(user_home_dir)[-1]
    findora_root = f'/data/findora'
    findora_root_mainnet = f'/data/findora/mainnet'
    findora_root_testnet = f'/data/findora/testnet'
    toolbox_location = os.path.join(user_home_dir, "validatortoolbox_fra")
    our_external_ip = getUrl()
    findora_menu = os.path.join(toolbox_location, "src", "messages", "framenu.txt")
    container_name = "findorad"
    migrate_dir = os.path.join(user_home_dir, "migrate")