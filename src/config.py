import os
import requests
import socket
from dotenv import load_dotenv
from colorama import Fore, Back, Style

def get_url(timeout=5) -> str:
    try:
        response = requests.get("https://api.ipify.org?format=json", timeout=timeout)
        response.raise_for_status()  # Raises a HTTPError if the response was unsuccessful

        # Parse the JSON response
        ip_data = response.json()
        result = ip_data["ip"]
    except requests.exceptions.RequestException:
        try:
            response = requests.get("https://ident.me", timeout=timeout)
            response.raise_for_status()  # Raises a HTTPError if the response was unsuccessful
            result = response.text
        except requests.exceptions.RequestException as x:
            print(type(x), x)
            result = "0.0.0.0"
    return result

class print_stuff:
    def __init__(self, reset: int = 0):
        self.reset = reset
        self.print_stars = f"{Fore.MAGENTA}*" * 93
        self.reset_stars = self.print_stars + Style.RESET_ALL

    def printStars(self) -> None:
        p = self.print_stars
        if self.reset:
            p = self.reset_stars
        print(p)

    def stringStars(self) -> str:
        p = self.print_stars
        if self.reset:
            p = self.reset_stars
        return p

    @classmethod
    def printWhitespace(self) -> None:
        print("\n" * 8)

class Config:
    def __init__(self):
        # Load environment variables from .env file
        load_dotenv()
        
        self.toolbox_version = "1.5.1"
        self.server_host_name = socket.gethostname()
        self.user_home_dir = os.path.expanduser("~")
        self.dotenv_file = f"{self.user_home_dir}/.findora.env"
        self.active_user_name = os.path.split(self.user_home_dir)[-1]
        self.findora_root = "/data/findora"
        self.findora_root_mainnet = f"{self.findora_root}/mainnet"
        self.findora_root_testnet = f"{self.findora_root}/testnet"
        self.toolbox_location = os.path.join(self.user_home_dir, "findora-toolbox")
        self.staker_memo_path = os.path.join(self.user_home_dir, "staker_memo")
        self.our_external_ip = get_url()
        self.container_name = "findorad"
        self.migrate_dir = os.path.join(self.user_home_dir, "migrate")
        self.fra_env = "prod"
        self.findora_backup = os.path.join(self.user_home_dir, "findora_backup")
        self.graphql_endpoint = "https://graph.findora.org"
        self.graphql_endpoint_backup = "https://mainnet2.graph.findora.org"
        
    def validate(self):
        essential_vars = [
            "toolbox_version",
            "server_host_name",
            "user_home_dir",
            "dotenv_file",
            "active_user_name",
            "findora_root",
            "findora_root_mainnet",
            "findora_root_testnet",
            "toolbox_location",
            "staker_memo_path",
            "our_external_ip",
            "container_name",
            "migrate_dir",
            "fra_env",
            "findora_backup",
            "graphql_endpoint",
            "graphql_endpoint_backup",
        ]
        for var in essential_vars:
            if not getattr(self, var):
                raise ValueError(f"Environment variable {var} is not set!")

# Usage
config = Config()
config.validate()  # Ensure essential configurations are set