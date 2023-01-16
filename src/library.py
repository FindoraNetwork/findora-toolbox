import subprocess, platform, os, time, argparse, json, shutil, pwd, getpass, requests, docker, dotenv, hashlib, psutil, cmd2
from datetime import datetime, timezone
from simple_term_menu import TerminalMenu
from collections import namedtuple
from datetime import datetime
from os import environ
from dotenv import load_dotenv
from colorama import Fore, Back, Style
from pprint import pprint
from config import easy_env_fra


class print_stuff:
    def __init__(self, reset: int = 0):
        self.reset = reset
        self.print_stars = "*" * 93
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


print_whitespace = print_stuff.printWhitespace
print_stars = print_stuff().printStars
string_stars = print_stuff().stringStars
print_stars_reset = print_stuff(reset=1).printStars
string_stars_reset = print_stuff(reset=1).stringStars


# loader intro splash screen
def loader_intro():
    standalone_option()
    p = f"""

 ▌ ▐· ▄▄▄· ▄▄▌  ▪  ·▄▄▄▄   ▄▄▄· ▄▄▄▄▄      ▄▄▄      ▄▄▄▄▄            ▄▄▌  ▄▄▄▄·       ▐▄• ▄ 
▪█·█▌▐█ ▀█ ██•  ██ ██▪ ██ ▐█ ▀█ •██  ▪     ▀▄ █·    •██  ▪     ▪     ██•  ▐█ ▀█▪▪      █▌█▌▪
▐█▐█•▄█▀▀█ ██▪  ▐█·▐█· ▐█▌▄█▀▀█  ▐█.▪ ▄█▀▄ ▐▀▀▄      ▐█.▪ ▄█▀▄  ▄█▀▄ ██▪  ▐█▀▀█▄ ▄█▀▄  ·██· 
 ███ ▐█ ▪▐▌▐█▌▐▌▐█▌██. ██ ▐█ ▪▐▌ ▐█▌·▐█▌.▐▌▐█•█▌     ▐█▌·▐█▌.▐▌▐█▌.▐▌▐█▌▐▌██▄▪▐█▐█▌.▐▌▪▐█·█▌
. ▀   ▀  ▀ .▀▀▀ ▀▀▀▀▀▀▀▀•  ▀  ▀  ▀▀▀  ▀█▄▀▪.▀  ▀     ▀▀▀  ▀█▄▀▪ ▀█▄▀▪.▀▀▀ ·▀▀▀▀  ▀█▄▀▪•▀▀ ▀▀
                                                                                            
▄▄▄▄·  ▄· ▄▌    ▄▄▄ . ▄▄▄· .▄▄ ·  ▄· ▄▌     ▐ ▄       ·▄▄▄▄  ▄▄▄ .                          
▐█ ▀█▪▐█▪██▌    ▀▄.▀·▐█ ▀█ ▐█ ▀. ▐█▪██▌    •█▌▐█▪     ██▪ ██ ▀▄.▀·                          
▐█▀▀█▄▐█▌▐█▪    ▐▀▀▪▄▄█▀▀█ ▄▀▀▀█▄▐█▌▐█▪    ▐█▐▐▌ ▄█▀▄ ▐█· ▐█▌▐▀▀▪▄                          
██▄▪▐█ ▐█▀·.    ▐█▄▄▌▐█ ▪▐▌▐█▄▪▐█ ▐█▀·.    ██▐█▌▐█▌.▐▌██. ██ ▐█▄▄▌                          
·▀▀▀▀   ▀ •      ▀▀▀  ▀  ▀  ▀▀▀▀   ▀ •     ▀▀ █▪ ▀█▄▀▪▀▀▀▀▀•  ▀▀▀                           
                                                                                            
    """
    print(p)
    return


def first_env_check(env_file, home_dir) -> None:
    if os.path.exists(env_file):
        load_var_file(env_file)
    else:
        os.system(f"touch {home_dir}/.easynode.env")
        load_var_file(env_file)


def set_var(env_file, key_name, update_name):
    if environ.get(key_name):
        dotenv.unset_key(env_file, key_name)
    dotenv.set_key(env_file, key_name, update_name)
    load_var_file(env_file)
    return


def compare_two_files(input1, input2) -> None:
    # open the files
    file1 = open(input1, "rb")
    file2 = open(input2, "rb")

    # generate their hashes
    hash1 = hashlib.md5(file1.read()).hexdigest()
    hash2 = hashlib.md5(file2.read()).hexdigest()

    # compare the hashes
    if hash1 == hash2:
        return True
    else:
        return False


def ask_yes_no(question: str) -> bool:
    yes_no_answer = ""
    while not yes_no_answer.startswith(("Y", "N")):
        yes_no_answer = input(f"{question}: ").upper()
    if yes_no_answer.startswith("Y"):
        return True
    return False


def load_var_file(var_file):
    if os.path.exists(var_file):
        load_dotenv(var_file, override=True)
    else:
        subprocess.run(["touch", var_file])


def finish_node():
    print(
        "* Thanks for using Easy Node Toolbox - Making everything Easy Mode!\n*\n* We serve up free tools and guides for validators every day.\n*\n* Check our guides out at https://guides.easynode.pro\n*\n"
        + "* Please consider supporting us one time or monthly at https://github.com/sponsors/easy-node-pro today!\n*\n* Goodbye!"
    )
    print_stars()
    raise SystemExit(0)


def pause_for_cause():
    print(Fore.MAGENTA)
    print_stars()
    print("* Press enter to return to the main menu.")
    print_stars()
    input()


def run_ubuntu_updater() -> None:
    os_upgrades()
    print()


def process_command(command: str) -> None:
    process = subprocess.Popen(command, shell=True)
    output, error = process.communicate()


def os_upgrades() -> None:
    upgrades = (
        "sudo apt update",
        "sudo apt upgrade -y",
        "sudo apt dist-upgrade -y",
        "sudo apt autoremove -y",
    )
    print_stars()
    for x in upgrades:
        process_command(x)
    print_stars()


def menu_error() -> None:
    standalone_option()
    print(
        "* "
        + Fore.RED
        + "WARNING"
        + Style.RESET_ALL
        + ": Only numbers are possible, please try your selection on the main menu once again.\n* Press enter to return to the menu."
    )
    print_stars()
    return


def menu_reboot_server() -> str:
    question = ask_yes_no(
        Fore.RED
        + "* WARNING: YOU WILL MISS BLOCKS WHILE YOU REBOOT YOUR ENTIRE SERVER.\n\n"
        + "* Reconnect after a few moments & Run the Validator Toolbox Menu again with: python3 ~/findora-toolbox/start.py\n"
        + Fore.WHITE
        + "* We will stop your container safely before restarting\n* Are you sure you would like to proceed with rebooting your server? (Y/N) "
    )
    if question:
        print(
            "* Stopping docker container for safety\n* Run toolbox after you reboot to get back online or start your container manually with `docker container start findorad` when you re-login!"
        )
        subprocess.call(["docker", "container", "stop", "findorad"])
        os.system("sudo reboot")
    else:
        print("Invalid option.")


def free_space_check(mount) -> str:
    ourDiskMount = get_mount_point(mount)
    _, _, free = shutil.disk_usage(ourDiskMount)
    freeConverted = str(converted_unit(free))
    return freeConverted


def disk_partitions(all=False):
    disk_ntuple = namedtuple("partition", "device mountpoint fstype")
    # Return all mounted partitions as a nameduple.
    # If all == False return physical partitions only.
    phydevs = []
    with open("/proc/filesystems", "r") as f:
        for line in f:
            if not line.startswith("nodev"):
                phydevs.append(line.strip())

    retlist = []
    with open("/etc/mtab", "r") as f:
        for line in f:
            if not all and line.startswith("none"):
                continue
            fields = line.split()
            device = fields[0]
            mountpoint = fields[1]
            fstype = fields[2]
            if not all and fstype not in phydevs:
                continue
            if device == "none":
                device = ""
            ntuple = disk_ntuple(device, mountpoint, fstype)
            retlist.append(ntuple)
    return retlist


def get_mount_point(pathname):
    pathname = os.path.normcase(os.path.realpath(pathname))
    parent_device = path_device = os.stat(pathname).st_dev
    while parent_device == path_device:
        mount_point = pathname
        pathname = os.path.dirname(pathname)
        if pathname == mount_point:
            break
        parent_device = os.stat(pathname).st_dev
    return mount_point


def converted_unit(n):
    symbols = ("K", "M", "G", "T", "P", "E", "Z", "Y")
    prefix = {}
    for i, s in enumerate(symbols):
        prefix[s] = 1 << (i + 1) * 10
    for s in reversed(symbols):
        if n >= prefix[s]:
            value = float(n) / prefix[s]
            return "%.1f%s" % (value, s)
    return "%sB" % n


def get_size(bytes, suffix="B"):
    factor = 1024
    for unit in ["", "K", "M", "G", "T", "P"]:
        if bytes < factor:
            return f"{bytes:.2f}{unit}{suffix}"
        bytes /= factor


def docker_check():
    try:
        status = subprocess.call(
            ["docker"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        if status == 0:
            print("* Docker ready.")
            print_stars()
            time.sleep(1)
        if status != 0:
            print(
                "* There's a problem with your docker. Are you in the `docker` group?\n* We will halt, make sure running the command `docker` works properly or try re-installing Docker.\n*\n* See: https://guides.easynode.pro/admin#docker-installation\n*"
            )
            print_stars()
            finish_node()
    except FileNotFoundError:
        print(
            "* Docker is not installed. Please install Docker per our guide and re-launch your installer."
        )
        print(
            "\n* See: https://guides.easynode.pro/admin#docker-installation - Install docker on this server and give the user access to continue.\n*"
        )
        print_stars()
        finish_node()


def all_sys_info():
    print("=" * 40, "System Information", "=" * 40)
    uname = platform.uname()
    print(f"System: {uname.system}")
    print(f"Node Name: {uname.node}")
    print(f"Release: {uname.release}")
    print(f"Version: {uname.version}")
    print(f"Machine: {uname.machine}")
    print(f"Processor: {uname.processor}")

    # Boot Time
    print("=" * 40, "Boot Time", "=" * 40)
    boot_time_timestamp = psutil.boot_time()
    bt = datetime.fromtimestamp(boot_time_timestamp)
    print(f"Boot Time: {bt.year}/{bt.month}/{bt.day} {bt.hour}:{bt.minute}:{bt.second}")

    # let's print CPU information
    print("=" * 40, "CPU Info", "=" * 40)
    # number of cores
    print("Physical cores:", psutil.cpu_count(logical=False))
    print("Total cores:", psutil.cpu_count(logical=True))
    # CPU frequencies
    cpufreq = psutil.cpu_freq()
    print(f"Max Frequency: {cpufreq.max:.2f}Mhz")
    print(f"Min Frequency: {cpufreq.min:.2f}Mhz")
    print(f"Current Frequency: {cpufreq.current:.2f}Mhz")
    # CPU usage
    print("CPU Usage Per Core:")

    # TODO: Does a Core start from 0? or 1? enumerate starts from 0.. check if we need i+1 to align !
    for i, percentage in enumerate(psutil.cpu_percent(percpu=True, interval=1)):
        print(f"Core {i}: {percentage}%")
    print(f"Total CPU Usage: {psutil.cpu_percent()}%")

    # Memory Information
    print("=" * 40, "Memory Information", "=" * 40)
    # get the memory details
    svmem = psutil.virtual_memory()
    print(f"Total: {get_size(svmem.total)}")
    print(f"Available: {get_size(svmem.available)}")
    print(f"Used: {get_size(svmem.used)}")
    print(f"Percentage: {svmem.percent}%")
    print("=" * 20, "SWAP", "=" * 20)
    # get the swap memory details (if exists)
    swap = psutil.swap_memory()
    print(f"Total: {get_size(swap.total)}")
    print(f"Free: {get_size(swap.free)}")
    print(f"Used: {get_size(swap.used)}")
    print(f"Percentage: {swap.percent}%")

    # Disk Information
    print("=" * 40, "Disk Information", "=" * 40)
    print("Partitions and Usage:")
    # get all disk partitions
    partitions = psutil.disk_partitions()
    for partition in partitions:
        print(f"=== Device: {partition.device} ===")
        print(f"  Mountpoint: {partition.mountpoint}")
        print(f"  File system type: {partition.fstype}")
        try:
            partition_usage = psutil.disk_usage(partition.mountpoint)
        except PermissionError:
            # this can be catched due to the disk that
            # isn't ready
            continue
        print(f"  Total Size: {get_size(partition_usage.total)}")
        print(f"  Used: {get_size(partition_usage.used)}")
        print(f"  Free: {get_size(partition_usage.free)}")
        print(f"  Percentage: {partition_usage.percent}%")
    # get IO statistics since boot
    disk_io = psutil.disk_io_counters()
    print(f"Total read: {get_size(disk_io.read_bytes)}")
    print(f"Total write: {get_size(disk_io.write_bytes)}")

    # Network information
    print("=" * 40, "Network Information", "=" * 40)
    # get all network interfaces (virtual and physical)
    if_addrs = psutil.net_if_addrs()
    for interface_name, interface_addresses in if_addrs.items():
        for address in interface_addresses:
            print(f"=== Interface: {interface_name} ===")
            if str(address.family) == "AddressFamily.AF_INET":
                print(f"  IP Address: {address.address}")
                print(f"  Netmask: {address.netmask}")
                print(f"  Broadcast IP: {address.broadcast}")
            elif str(address.family) == "AddressFamily.AF_PACKET":
                print(f"  MAC Address: {address.address}")
                print(f"  Netmask: {address.netmask}")
                print(f"  Broadcast MAC: {address.broadcast}")
    # get IO statistics since boot
    net_io = psutil.net_io_counters()
    print(f"Total Bytes Sent: {get_size(net_io.bytes_sent)}")
    print(f"Total Bytes Received: {get_size(net_io.bytes_recv)}")


def coming_soon():
    print("* This option isn't available on your system, yet!")
    print_stars()


def container_running(container_name) -> None:
    # create client object to connect
    client = docker.from_env()
    # Get a list of all containers
    containers = client.containers.list()
    # Search for the container by name
    container = next(filter(lambda c: c.name == container_name, containers), None)
    if container is not None and container.status == "running":
        return True
    else:
        return False


def set_main_or_test() -> None:
    if not environ.get("FRA_NETWORK"):
        subprocess.run("clear")
        print_stars()
        print(
            "* Setup config not found, Does this run on mainnet or testnet?                              *"
        )
        print_stars()
        print(
            "* [0] - Mainnet                                                                             *"
        )
        print(
            "* [1] - Testnet                                                                             *"
        )
        print_stars()
        menu_options = [
            "[0] Mainnet",
            "[1] Testnet",
        ]
        terminal_menu = TerminalMenu(menu_options, title="Mainnet or Testnet")
        results = terminal_menu.show()
        if results == 0:
            set_var(easy_env_fra.dotenv_file, "FRA_NETWORK", "mainnet")
            network = "mainnet"
        if results == 1:
            set_var(easy_env_fra.dotenv_file, "FRA_NETWORK", "testnet")
            network = "testnet"
        subprocess.run("clear")
    else:
        network = environ.get("FRA_NETWORK")
    return network


def menu_findora() -> None:
    update = menu_topper()
    print("* EasyNode.PRO Findora Validator Toolbox Menu Options:")
    print("*")
    print(
        "*   1 -  Show 'curl' stats info    - Run this to show your local curl stats!"
    )
    print("*   2 -  Show 'fn' stats info      - Run this to show your local fn stats!")
    print("*   3 -  Claim Pending FRA         - Claim all of your unclaimed FRA now")
    print("*   4 -  Transfer FRA              - Send FRA to another fra address now")
    print(
        "*   5 -  Set Transfer Options Menu - Configure your preferred send wallet & privacy"
    )
    print(
        "*   6 -  Change Rate or Info Menu  - Change your rate. Change info coming soon."
    )
    print(
        "*   7 -  Update fn Application     - Pull update for the wallet application, fn"
    )
    print(
        f"*                                   {Fore.CYAN}{Back.RED}The Danger Zone:{Style.RESET_ALL}{Fore.MAGENTA}"
    )
    findora_container_update(update)
    print(
        "*   9 -  Run Safety Clean          - Stop your container, reset and download database fresh"
    )
    print("*  10 -  Update Operating System   - Update Ubuntu Operating System Files")
    print(
        f"*                                   {Fore.BLUE}{Back.YELLOW}Informational Section:{Style.RESET_ALL}{Fore.MAGENTA}"
    )
    print("*  11 -  Show system disk info     - Current drive space status")
    print(
        "*  12 -  TMI about your Server     - Seriously a lot of info about this server"
    )
    print(
        "*  13 -  Instructions on Migrating - Run this to read info on migrating to this server."
    )
    print_stars()
    if migration_check():
        print_migrate()
    print(
        "* 999 -  Reboot Server             - "
        + Fore.YELLOW
        + Back.RED
        + "WARNING: You will miss blocks during a reboot!"
        + Style.RESET_ALL
        + Fore.MAGENTA
    )
    print("*   0 -  Exit Application          - Goodbye!")
    print_stars()
    return


def get_curl_stats() -> None:
    standalone_option()
    print(Fore.GREEN)
    try:
        response = requests.get("http://localhost:26657/status")
        stats = json.loads(response.text)
        print_stars()
        pprint(stats)
    except subprocess.CalledProcessError as err:
        print(f"* No response from the rpc. Error: {err}")
    print(Fore.MAGENTA)


def capture_stats() -> None:
    try:
        response = requests.get("http://localhost:26657/status")
        stats = json.loads(response.text)
        return stats
    except:
        print("* No response from the rpc.\n* Is Docker running?")
        finish_node()


def refresh_fn_stats() -> None:
    standalone_option()
    try:
        output = subprocess.check_output(["fn", "show"])
        output = output.decode().replace("b'", "")
        print(output)
    except subprocess.CalledProcessError as err:
        print(
            f"* Error, no response from local API, try your command again or check your fn stats to see if there's an issue.\n* Error: {err}"
        )


def standalone_option():
    # For menu options that can run on their own, always clear and stars first.
    print(Fore.MAGENTA)
    subprocess.run("clear")
    print_stars()
    return


def claim_findora_rewards() -> None:
    standalone_option()
    try:
        output = subprocess.call(
            ["fn", "claim"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        print(
            f"* Claim all pending completed, refresh your stats after the next block."
        )
    except subprocess.CalledProcessError as err:
        print(
            f"* Error, no response from local API, try your command again or check your fn stats to see if there's an issue.\n* Error: {err}"
        )


def get_total_send(our_fn_stats) -> None:
    # Get fra input and process
    total = input(
        f'* Current balance is: {Fore.GREEN}{our_fn_stats["Balance"]}{Fore.MAGENTA}\n*\n* How much FRA total would you like to send from your validator? '
    )
    total2 = input(
        f"*\n* Please re-enter the amount of FRA you would like to transfer for verification: "
    )
    if total == total2:
        return total
    else:
        input("*\n* Balances did not match, try again. Press enter to try again.")
        get_total_send(our_fn_stats)


def get_receiver_address() -> None:
    # IF we've already got it, check it or ask
    if environ.get("RECEIVER_WALLET"):
        question = ask_yes_no(
            f'* We have {Fore.YELLOW}{environ.get("RECEIVER_WALLET")}{Fore.MAGENTA} on file. Would you like to send to this address? (Y/N)'
        )
        if question:
            return environ.get("RECEIVER_WALLET")
    address = input(
        f"*\n* Please input the fra1 address you would like to send your FRA: "
    )
    if address[:4] != "fra1" or len(address) != 62:
        input(
            f"* {address} does not look like a valid fra1 address, please retry. Press enter to return to try again."
        )
        get_receiver_address()
    if address == environ.get("RECEIVER_WALLET"):
        print(
            "* This is already your saved wallet, try again with a new wallet to update this option."
        )
        return environ.get("RECEIVER_WALLET")
    address2 = input(
        f"*\n* Please re-input the fra1 address you would like to send your FRA for verification: "
    )
    if address == address2:
        return address
    else:
        input("* Address did not match, try again. Press enter to try again.")
        get_receiver_address()


def get_privacy_option() -> None:
    # IF we've already got it, check it or ask
    if environ.get("PRIVACY"):
        question = ask_yes_no(
            f'* We have Privacy = {environ.get("PRIVACY")} on file, Would you like to use this option for this transaction as well? (Y/N) '
        )
        if question:
            return environ.get("PRIVACY")
    privacy = ask_yes_no("*\n* Would you like this to be a private transaction? (Y/N) ")
    if privacy:
        return "True"
    else:
        return "False"


def set_privacy(receiver_address, privacy) -> None:
    # if these are already set, bypass
    if receiver_address == environ.get("RECEIVER_WALLET") and privacy == environ.get(
        "PRIVACY"
    ):
        return
    # ask and set
    print_stars()
    print(
        f'*\n* Currently used options:\n* Address: {Fore.YELLOW}{receiver_address}{Fore.MAGENTA}\n* Privacy {privacy}\n* Express send: {environ.get("SEND_EXPRESS")}'
    )
    question = ask_yes_no(
        f"*\n* Would you like to save this wallet and privacy setting as default options to bypass all these questions next time? (Y/N) "
    )
    if question:
        set_var(easy_env_fra.dotenv_file, "SEND_EXPRESS", "True")
        set_var(easy_env_fra.dotenv_file, "RECEIVER_WALLET", receiver_address)
        set_var(easy_env_fra.dotenv_file, "PRIVACY", f"{privacy}")
    print(
        f'* Currently saved options:\n* Address: {Fore.YELLOW}{receiver_address}{Fore.MAGENTA}\n* Privacy {privacy}\n* Express send: {environ.get("SEND_EXPRESS")}'
    )
    return


def pre_send_findora() -> None:
    # Get balance
    our_fn_stats = get_fn_stats()
    send_total = get_total_send(our_fn_stats)
    express = environ.get("SEND_EXPRESS")
    convert_send_total = str(int(float(send_total) * 1000000))
    if express == "True":
        send_findora(
            convert_send_total,
            send_total,
            environ.get("RECEIVER_WALLET"),
            environ.get("PRIVACY"),
        )
        return
    receiver_address = get_receiver_address()
    privacy = get_privacy_option()
    if privacy == "True":
        # Send tx, with privacy
        question = ask_yes_no(
            f"*\n* We are going to send {Fore.GREEN}{send_total}{Fore.MAGENTA} to address {Fore.YELLOW}{receiver_address}{Fore.MAGENTA} with Privacy set to True.\n*\n* Press Y to send or N to return to the main menu. (Y/N) "
        )
        if question:
            send_findora(convert_send_total, send_total, receiver_address, "True")
        else:
            return
    else:
        # Send tx regular
        question = ask_yes_no(
            f"*\n* We are going to send {Fore.GREEN}{send_total}{Fore.MAGENTA} to address {Fore.YELLOW}{receiver_address}{Fore.MAGENTA} with Privacy set to False.\n*\n* Press Y to send or N to return to the main menu. (Y/N) "
        )
        send_findora(convert_send_total, send_total, receiver_address, "False")
    set_privacy(receiver_address, privacy)


def send_findora(send_amount, fra_amount, to_address, privacy="False") -> None:
    # transfer if privacy on
    try:
        if privacy == "True":
            subprocess.call(
                [
                    "fn",
                    "transfer",
                    "--amount",
                    send_amount,
                    "-T",
                    to_address,
                    "--confidential-amount",
                    "--confidential-type",
                ],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        else:
            subprocess.call(
                ["fn", "transfer", "--amount", send_amount, "-T", to_address],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        print(
            f"{Fore.MAGENTA}*\n* Sent {Fore.GREEN}{fra_amount}{Fore.MAGENTA} to {Fore.YELLOW}{to_address}{Fore.MAGENTA} with privacy = {privacy}\n*\n* Please note it will take at least a block to get updated stats in toolbox.\n*\n*"
        )
    except subprocess.CalledProcessError as err:
        print(
            f"{Fore.MAGENTA}* Error sending transaction:\n* {err}\n* Please try again later."
        )
    return


def change_rate(our_fn_stats):
    standalone_option()
    print(f"* Current Rate: {our_fn_stats['Commission Rate']}")
    answer = input(
        "* What would you like the new rate to be?\n* Please use findora notation, example for 5% fees use: 0.05\n* Enter your new rate now: "
    )
    answer2 = input("* Please re-enter your new rate to confirm: ")
    if answer == answer2:
        question = ask_yes_no(
            f"* Are you sure you want to change your rate to {float(answer)*100}%? (Y/N) "
        )
        if question:
            subprocess.call(
                ["fn", "staker-update", "-R", answer],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            print(f"* Your rate change to {float(answer)*100}% has been sent!")
        else:
            print("* You answered No, returning to main menu.")
    else:
        print("* Your answers didn't match, returning to main menu. ")
    return


class MemoUpdater(cmd2.Cmd):
    def __init__(self, our_fn_stats):
        super().__init__()
        self.our_fn_stats = our_fn_stats

    def do_update(self, arg):
        print_stars()
        print("* Current Settings: ")
        print_stars()
        memo_items = {key: value[2:-1] for key, value in self.our_fn_stats['memo'].items()}
        options = []
        for key, value in memo_items.items():
            options.append(f'{key} - {value}')
        options.append("Exit")
        while True:
            choice = self.select(options)
            if choice == "Exit":
                return memo_items
            key = choice.split(" - ")[0]
            new_value = input('Enter the new value: ')
            memo_items[key] = new_value
            options[options.index(choice)] = f'{key} - {new_value}'
            print(f'Successfully updated "{key}" to "{new_value}"')
        return memo_items


def change_memo(our_fn_stats):
    updater = MemoUpdater(our_fn_stats)
    # allow edit one by one, then have commit changes at the end?
    memo_items = updater.do_update(None)
    # show current staker_memo info, update records and send
    print_stars()
    memo_items_json = json.dumps(memo_items)
    print('* Here is your updated staker_memo information for verifictaion before sending changes:')
    print(memo_items)
    print_stars()
    question = ask_yes_no("* Overwrite ~/staker_memo with your changes and send on chain update now? (Y/N) ")
    if question:
        with open(easy_env_fra.staker_memo_path, 'w') as file:
            file.write(memo_items_json)
        subprocess.call(['fn', 'staker-update', '-M', memo_items_json])
    print_stars()
    return


def change_validator_info():
    # fix this menu, it's nuts. Always does change_rate
    standalone_option()
    our_fn_stats = get_fn_stats()
    if "Self Delegation" not in our_fn_stats:
        print(
            f"* You have not created your validator yet. Please exit, stake with your validator wallet and send the create validator command.\n* See our post install guide at https://guides.easynode.pro/findora/post#validator-wallet-commands\n*\n* Press enter to return to the main menu."
        )
        return
    # Change the rate & staker memo info
    print(f"* Which validator options would you like to update?")
    change_info_menu = [
        "[0] - Change Commission Rate",
        "[1] - Change staker_memo Information",
        "[2] - Exit to Main Menu",
    ]
    print_stars()
    terminal_menu = TerminalMenu(
        change_info_menu, title="* What would you like to update today? "
    )
    response = terminal_menu.show()
    # add logic for choices here pass our_fn_stats to #2
    if response == 0:
        change_rate(our_fn_stats)
    if response == 1:
        change_memo(our_fn_stats)
    if response == 2:
        return
    return


def check_address_input(address) -> None:
    if address[:4] != "fra1" or len(address) != 62:
        input(
            f"* {address} does not look like a valid fra1 address, please retry. Press enter to return to the menu."
        )
        return
    if address == environ.get("RECEIVER_WALLET"):
        input(
            "* This is already your saved wallet, try again with a new wallet to update this option. Press enter to return to the menu."
        )
        return
    address2 = input(
        f"*\n* Please re-input the fra1 address you would like to send your FRA for verification: "
    )
    if address == address2:
        set_var(easy_env_fra.dotenv_file, "RECEIVER_WALLET", address)
        input(f"* Wallet updated to {Fore.YELLOW}{address}{Fore.MAGENTA}")
        return
    else:
        input(
            "* Address did not match, try again with matching info. Press enter to return to the menu."
        )
        return


def set_send_options() -> None:
    # Give'm some options!
    print(Fore.MAGENTA)
    standalone_option()
    print(
        f"* Select a send tx option to change: \n*\n* 0. Express Wallet - Currently {Fore.YELLOW}{environ.get('RECEIVER_WALLET')}{Fore.MAGENTA}\n* 1. Privacy Option - Change current privacy option: {environ.get('PRIVACY')}\n* 2. Express Option - Change current express option: {environ.get('SEND_EXPRESS')}\n* 3. Exit - Return to Main Menu\n*"
    )
    menu_options = [
        "* [0] - Set Wallet",
        "* [1] - Set Privacy",
        "* [2] - Set Express",
        "* [3] - Exit to Main Menu",
    ]
    print_stars()
    terminal_menu = TerminalMenu(
        menu_options, title="* Which option would you like to update?"
    )
    menu_option = terminal_menu.show()
    if menu_option == 0:
        address = input(
            f"*\n* Please input the fra1 address you would like to send your FRA: "
        )
        check_address_input(address)
    if menu_option == 1:
        print(f"* Select an option. Privacy enabled on transactions, True or False: ")
        menu_options = ["* [0] - True", "* [1] - False"]
        terminal_menu = TerminalMenu(
            menu_options, title="* Would you like private transactions? "
        )
        sub_menu_option = terminal_menu.show()
        if sub_menu_option == 0:
            set_var(easy_env_fra.dotenv_file, "PRIVACY", "True")
        if sub_menu_option == 1:
            set_var(easy_env_fra.dotenv_file, "PRIVACY", "False")
    if menu_option == 2:
        print(
            f"* Select an option. Express enabled to auto send with your saved options, would you like it enabled or disabled? "
        )
        menu_options = ["* [0] - True", "* [1] - False"]
        terminal_menu = TerminalMenu(
            menu_options,
            title=f'* Express option currently set to {environ.get("SEND_EXPRESS")}. Would you like to switch this?',
        )
        sub_menu_2_option = terminal_menu.show()
        if sub_menu_2_option == 0:
            set_var(easy_env_fra.dotenv_file, "SEND_EXPRESS", "True")
        if sub_menu_2_option == 1:
            set_var(easy_env_fra.dotenv_file, "SEND_EXPRESS", "False")
    if menu_option == 3:
        return
    set_send_options()


def server_disk_check() -> None:
    print_stars_reset()
    print("* Here are all of your mount points: ")
    for part in disk_partitions():
        print(part)
    print_stars()
    total, used, free = shutil.disk_usage(easy_env_fra.findora_root)
    total = str(converted_unit(total))
    used = str(converted_unit(used))
    print(
        "Disk: "
        + str(easy_env_fra.findora_root)
        + "\n"
        + free_space_check(easy_env_fra.findora_root)
        + " Free\n"
        + used
        + " Used\n"
        + total
        + " Total"
    )


def get_container_version(url) -> None:
    response = requests.get(url)
    return response.text


def findora_container_update(update) -> None:
    if update:
        print(
            f"{Fore.CYAN}*   8 -  Update Findora Container  - Pull & Restart the latest container from Findora{Fore.MAGENTA}"
        )
        return
    else:
        print(
            "*   8 -  Update Findora Container  - Pull & Restart the latest container from Findora"
        )
        return


def findora_gwei_convert(findora):
    fra_amount = int(findora) / 1000000
    return fra_amount


def get_fn_stats():
    output = subprocess.check_output(["fn", "show"])
    json_string = (
        output.decode()
        .replace("b'", "")
        .replace("\x1b[31;01m", "")
        .replace("\x1b[00m", "")
    )

    lines = json_string.split("\n")

    fn_info = {}
    memo = {}
    if int(lines[17].split()[1][:-1]) == 0:
        fn_info["Network"] = lines[1]
        fn_info["Current Block"] = lines[29].split()[1][:-1]
        fn_info[
            "Balance"
        ] = f"{'{:,}'.format(round(findora_gwei_convert(int(lines[10].split()[0])), 2))} FRA"
        fn_info["Proposed Blocks"] = "0"
    else:
        fn_info["Network"] = lines[1]
        fn_info["Current Block"] = lines[34].split()[1][:-1]
        fn_info["Proposed Blocks"] = lines[36].split()[1]
        fn_info[
            "Self Delegation"
        ] = f"{'{:,}'.format(round(findora_gwei_convert(int(lines[17].split()[1][:-1])), 2))} FRA"
        fn_info[
            "Balance"
        ] = f"{'{:,}'.format(round(findora_gwei_convert(int(lines[10].split()[0])), 2))} FRA"
        fn_info[
            "Unclaimed Rewards"
        ] = f"{'{:,}'.format(round(findora_gwei_convert(int(lines[25].split()[1][:-1])), 2))} FRA"
        fn_info[
            "Pool Unclaimed FRA"
        ] = f"{'{:,}'.format(round(findora_gwei_convert(int(lines[51].split()[1][:-1])), 2))} FRA"
        fn_info["Server Rank"] = lines[45].split()[1][:-1]
        fn_info["Delegator Count"] = lines[66].split()[1]
        fn_info["Commission Rate"] = f"{int(lines[47][:-1])/100}%"
        memo["name"] = lines[53].partition('"name":')[2][:-1]
        memo["desc"] = lines[54].partition('"desc":')[2][:-1]
        memo["website"] = lines[55].partition('"website":')[2][:-1]
        memo["logo"] = lines[56].partition('"logo":')[2]
        fn_info["memo"] = memo

    return fn_info


def menu_topper() -> None:
    try:
        Load1, Load5, Load15 = os.getloadavg()
        curl_stats = capture_stats()
        now = datetime.now(timezone.utc)
        fra = findora_gwei_convert(
            curl_stats["result"]["validator_info"]["voting_power"]
        )
        our_version = get_container_version("http://localhost:8668/version")
        our_fn_stats = get_fn_stats()
        try:
            our_fn_stats.pop("memo")
        except KeyError as err:
            pass
        online_version = get_container_version(
            f'https://{easy_env_fra.fra_env}-{environ.get("FRA_NETWORK")}.{easy_env_fra.fra_env}.findora.org:8668/version'
        )
    except TimeoutError as e:
        our_version = "No Response"
        online_version = "No Response"
        print_stars()
        print(f"* Timeout error: {e}")
        print_stars()
        input()
    subprocess.run("clear")
    print(Fore.MAGENTA)
    print_stars()
    print(
        f"{Style.RESET_ALL}{Fore.MAGENTA}* {Fore.MAGENTA}findora-toolbox for Findora FRA Validators by Easy Node"
        + f"   v{easy_env_fra.easy_version}{Style.RESET_ALL}{Fore.MAGENTA}   https://easynode.pro *"
    )
    print_stars()
    print(
        f"* Server Hostname & IP:      {easy_env_fra.server_host_name}{Style.RESET_ALL}{Fore.MAGENTA}"
        + f" - {Fore.YELLOW}{easy_env_fra.our_external_ip}{Style.RESET_ALL}{Fore.MAGENTA}"
    )
    print(
        f"* Public Address:            {curl_stats['result']['validator_info']['address']}"
    )
    if our_fn_stats["Network"] == "https://prod-mainnet.prod.findora.org":
        print(f"* Network:                   Mainnet")
    if our_fn_stats["Network"] == "https://prod-testnet.prod.findora.org":
        print(f"* Network:                   Testnet")
    our_fn_stats.pop("Network")
    print(
        f"* Current FRA Staked:        {Fore.CYAN}{'{:,}'.format(round(fra, 2))}{Fore.MAGENTA} FRA"
    )
    if curl_stats["result"]["sync_info"]["catching_up"] == "False":
        print(
            f"* Catching Up:                    {Fore.RED}{curl_stats['result']['sync_info']['catching_up']}{Fore.MAGENTA}"
        )
    else:
        print(
            f"* Catching Up:               {Fore.GREEN}{curl_stats['result']['sync_info']['catching_up']}{Fore.MAGENTA}"
        )
    print(
        f"* Local Latest Block:        {curl_stats['result']['sync_info']['latest_block_height']}  * Remote Latest Block:        {our_fn_stats['Current Block']}"
    )
    our_fn_stats.pop("Current Block")
    print(f"* Proposed Blocks:           {our_fn_stats['Proposed Blocks']}")
    our_fn_stats.pop("Proposed Blocks")
    for i in our_fn_stats:
        spaces = "                         "
        print(f"* {i}: {spaces[len(i):]}{our_fn_stats[i]}")
    print(
        f"* Latest Block Time:         {curl_stats['result']['sync_info']['latest_block_time'][:-11]}"
    )
    print(f"* Current Time UTC:          {now.strftime('%Y-%m-%dT%H:%M:%S')}")
    print(
        f"* Current Disk Space Free:   {Fore.BLUE}{free_space_check(easy_env_fra.findora_root): >6}{Style.RESET_ALL}{Fore.MAGENTA}"
    )
    print(f"* Current Container Build:   {our_version.split()[1]}")
    if online_version != our_version:
        print(f"* Update Available:          {online_version}")
        update = True
    else:
        update = False
    print_stars()
    print(
        f"* CPU Load Averages: {round(Load1, 2)} over 1 min, {round(Load5, 2)} over 5 min, {round(Load15, 2)} over 15 min"
    )
    print_stars()
    return update


def rescue_menu() -> None:
    menu_options = {
        0: finish_node,
        1: get_curl_stats,
        2: run_container_update,
        3: run_clean_script,
    }
    print(
        "* We still don't detect a running container. Here are your options currently:"
        + "\n* 1 - CURL stats - Keep checking stats"
        + "\n* 2 - update_version script - Run the update version script as a first option for recovery."
        + "\n* 3 - safety_clean script - Run the safety_clean script as a last option to reset database data and reconfigure server."
        + "\n* 0 - Exit and manually troubleshoot"
    )
    print_stars()
    try:
        option = int(input("Enter your option: "))
    except ValueError:
        menu_error()
        rescue_menu()
    subprocess.run("clear")
    menu_options[option]()
    rescue_menu()


def update_findora_container(skip) -> None:
    print(
        "* Running the update and restart may cause missed blocks, beware before proceeding!"
    )
    if skip:
        answer = True
    else:
        answer = ask_yes_no(
            "* Are you sure you want to check for an upgrade and restart? (Y/N) "
        )
    if answer:
        subprocess.call(
            [
                "wget",
                "-O",
                f"/tmp/update_{environ.get('FRA_NETWORK')}.sh",
                f"https://raw.githubusercontent.com/easy-node-pro/findora-validator-scripts/main/easy_update_{environ.get('FRA_NETWORK')}.sh",
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        subprocess.run("clear")
        print(
            "* We will show the output of the upgrade & restart now, this may miss a block(s) depending on your timing."
        )
        subprocess.call(
            ["bash", "-x", f"/tmp/update_{environ.get('FRA_NETWORK')}.sh"],
            cwd=easy_env_fra.user_home_dir,
        )
        if container_running(easy_env_fra.container_name):
            print_stars()
            print(
                "* Your container is restarted and back online. Press enter to return to the main menu."
            )
            pause_for_cause()
            run_findora_menu()
        else:
            print_stars()
            print(
                "* Your container was restarted but there was a problem bringing it back online."
                + "\n* We will load our rescue menu with the safety_clean script as an option."
                + "\n* You can exit out and check your docker logs with `docker logs findorad` to see if there's a file or permissions issue."
                + "\n* Running safety_clean can help resolve most issues since update didn't bring you back online."
            )
            pause_for_cause
            rescue_menu()
    return


def migration_update() -> None:
    subprocess.call(
        [
            "wget",
            "-O",
            f"/tmp/update_{environ.get('FRA_NETWORK')}.sh",
            f"https://raw.githubusercontent.com/easy-node-pro/findora-validator-scripts/main/easy_update_{environ.get('FRA_NETWORK')}.sh",
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    subprocess.call(
        ["bash", "-x", f"/tmp/update_{environ.get('FRA_NETWORK')}.sh"],
        cwd=easy_env_fra.user_home_dir,
    )


def update_fn_wallet() -> None:
    print("* This option upgrades the fn wallet application.")
    answer = ask_yes_no("* Do you want to upgrade fn now? (Y/N) ")
    if answer:
        subprocess.call(
            [
                "wget",
                "-O",
                f"/tmp/fn_update_{environ.get('FRA_NETWORK')}.sh",
                f"https://raw.githubusercontent.com/easy-node-pro/findora-validator-scripts/main/fn_update_{environ.get('FRA_NETWORK')}.sh",
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        subprocess.run("clear")
        print("* We will show the output of the upgrade now.")
        subprocess.call(
            ["bash", "-x", f"/tmp/fn_update_{environ.get('FRA_NETWORK')}.sh"],
            cwd=easy_env_fra.user_home_dir,
        )


def run_clean_script() -> None:
    print(
        "* Running the update and restart may cause missed blocks, beware before proceeding!"
        + "\n* This option runs Safety Clean stopping your container and reloading all data.\n* Run as a last resort in troubleshooting."
    )
    answer = ask_yes_no("* Do you want to run safety clean now? (Y/N) ")
    if answer:
        subprocess.call(
            [
                "wget",
                "-O",
                f"/tmp/safety_clean_{environ.get('FRA_NETWORK')}.sh",
                f"https://raw.githubusercontent.com/easy-node-pro/findora-validator-scripts/main/safety_clean_{environ.get('FRA_NETWORK')}.sh",
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        subprocess.run("clear")
        print("* We will show the output of the reset now.")
        subprocess.call(
            ["bash", "-x", f"/tmp/safety_clean_{environ.get('FRA_NETWORK')}.sh"],
            cwd=easy_env_fra.user_home_dir,
        )
        if container_running(easy_env_fra.container_name):
            print_stars()
            print(
                "* Your container is restarted and back online. Press enter to return to the main menu."
            )
            input()
            run_findora_menu()
        else:
            print_stars()
            print(
                "* Your container was restarted but there was a problem bringing it back online.\n*"
                + "\n* Starting the rescue menu now. Press enter to load the menu or ctrl+c to quit and manually troubleshoot."
            )
            input()
            rescue_menu()


def create_staker_memo() -> None:
    if os.path.exists(f"{easy_env_fra.user_home_dir}/staker_memo") is False:
        shutil.copy(
            f"{easy_env_fra.toolbox_location}/src/bin/staker_memo",
            f"{easy_env_fra.user_home_dir}",
        )


def run_findora_installer(network) -> None:
    subprocess.call(
        [
            "wget",
            f"https://raw.githubusercontent.com/easy-node-pro/findora-validator-scripts/main/easy_install_{network}.sh",
            "-O",
            f"/tmp/install_{network}.sh",
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    standalone_option()
    print(
        "* We will show the output of the installation, this will take some time to download and unpack.\n* Starting Findora installation now."
    )
    print_stars()
    time.sleep(1)
    print_stars()
    subprocess.call(
        ["bash", "-x", f"/tmp/install_{network}.sh"],
        cwd=easy_env_fra.user_home_dir,
    )
    print_stars()
    create_staker_memo()
    print(
        "* Setup has completed. Once you are synced up (catching_up=False) you are ready to create your "
        + "validator on-chain or migrate from another server onto this server."
    )
    pause_for_cause()


def menu_install_findora(network) -> None:
    # Run installer ya'll!
    print(
        "* We've detected that Docker is properly installed for this user, excellent!"
        + f"\n* But...it doesn't look like you have Findora {network} installed."
        + "\n* We will setup Findora validator on this server with a brand new wallet and start syncing with the blockchain."
    )
    answer = ask_yes_no(f"* Do you want to install {network} now? (Y/N) ")
    if answer:
        run_findora_installer(network)
    else:
        raise SystemExit(0)


def run_ubuntu_updates() -> None:
    question = ask_yes_no(
        "* You will miss blocks while upgrades run.\n* Are you sure you want to run updates? (Y/N) "
    )
    if question:
        subprocess.run("clear")
        print_stars()
        print("* Stopping docker container for safety")
        subprocess.call(["docker", "container", "stop", "findorad"])
        run_ubuntu_updater()
        print_stars()
        print("* Restarting findorad container")
        subprocess.call(["docker", "container", "start", "findorad"])
        refresh_fn_stats()
    else:
        return


def chown_dir(root_dir, user, group) -> None:
    for root, dirs, files in os.walk(root_dir):
        for f in files:
            os.chown(os.path.join(root, f), user, group)
        for d in dirs:
            os.chown(os.path.join(root, d), user, group)


def get_uid() -> None:
    user_name = getpass.getuser()
    user_info = pwd.getpwnam(user_name)
    uid = user_info.pw_uid
    return uid


def migration_instructions():
    # path doesn't exist, explain migration process.
    print(
        f"* We didn't locate a folder at {easy_env_fra.migrate_dir}\n*\n* Exit the toolbox, then:"
        + f"\n* 1. Make a folder named {easy_env_fra.migrate_dir}\n* 2. Add your tmp.gen.keypair file into the folder"
        + "\n* 3. Add your config folder containing your priv_validator_key.json file into ~/migrate"
        + "\n* 4. If this server is catching_up=False, you can shut off the old server and relaunch the menu here to migrate."
        + "\n*\n* The goal is to avoid double signing and a 5% slashing fee!!!\n*\n* Load your files and run this option again!"
    )


def migrate_to_server() -> None:
    if os.path.exists(f"{easy_env_fra.migrate_dir}"):
        # check for tmp.gen.keypair and priv_validator_key.json in ~/migrate
        print("* You have a migrate folder, checking for files.")
        if (
            os.path.exists(f"{easy_env_fra.migrate_dir}/tmp.gen.keypair")
            and os.path.exists(
                f"{easy_env_fra.migrate_dir}/config/priv_validator_key.json"
            )
            or os.path.exists(f"{easy_env_fra.migrate_dir}/priv_validator_key.json")
        ):
            print(
                f"* {easy_env_fra.migrate_dir}/tmp.gen.keypair found!\n* {easy_env_fra.migrate_dir}/config/priv_validator_key.json found!"
                + "\n* All required files in place, ready for upgrade!"
            )
            # Ask to start migration, warn about double sign again, again
            print_stars()
            answer = ask_yes_no(
                "* Are you sure your old server is shut down? Files to migrate have been detected."
                + "\n* One last time, are you sure you want to migrate and start-up now? (Y/N) "
            )
            if answer:
                print_stars()
                # start installing
                print("* Copying Files...")
                # stop service
                subprocess.call(["docker", "container", "stop", "findorad"])
                # move files
                if os.path.exists(
                    f'{easy_env_fra.findora_root}/{environ.get("FRA_NETWORK")}/{environ.get("FRA_NETWORK")}_node.key'
                ):
                    os.remove(
                        f'{easy_env_fra.findora_root}/{environ.get("FRA_NETWORK")}/{environ.get("FRA_NETWORK")}_node.key'
                    )
                shutil.move(
                    f"{easy_env_fra.migrate_dir}/tmp.gen.keypair",
                    f'{easy_env_fra.findora_root}/{environ.get("FRA_NETWORK")}/{environ.get("FRA_NETWORK")}_node.key',
                )
                os.remove(
                    f'{easy_env_fra.findora_root}/{environ.get("FRA_NETWORK")}/tendermint/config/priv_validator_key.json'
                )
                if os.path.exists(
                    f"{easy_env_fra.migrate_dir}/priv_validator_key.json"
                ):
                    shutil.move(
                        f"{easy_env_fra.migrate_dir}/priv_validator_key.json",
                        f'{easy_env_fra.findora_root}/{environ.get("FRA_NETWORK")}/tendermint/config/priv_validator_key.json',
                    )
                elif os.path.exists(
                    f"{easy_env_fra.migrate_dir}/config/priv_validator_key.json"
                ):
                    shutil.move(
                        f"{easy_env_fra.migrate_dir}/config/priv_validator_key.json",
                        f'{easy_env_fra.findora_root}/{environ.get("FRA_NETWORK")}/tendermint/config/priv_validator_key.json',
                    )
                else:
                    print(
                        "* Welp, somehow we didn't find a priv_validator_key.json to migrate."
                        + "\n* You'll have to get your key into the config folder and run a safety clean."
                    )
                node_mnemonic = subprocess.getoutput(
                    f"cat {easy_env_fra.findora_root}/{environ.get('FRA_NETWORK')}/{environ.get('FRA_NETWORK')}_node.key "
                    + "| grep 'Mnemonic' | sed 's/^.*Mnemonic:[^ ]* //'"
                )
                os.remove(
                    f"{easy_env_fra.findora_root}/{environ.get('FRA_NETWORK')}/node.mnemonic"
                )
                subprocess.call(
                    [
                        "touch",
                        f"{easy_env_fra.findora_root}/{environ.get('FRA_NETWORK')}/node.mnemonic",
                    ]
                )
                with open(
                    f"{easy_env_fra.findora_root}/{environ.get('FRA_NETWORK')}/node.mnemonic",
                    "w",
                ) as file:
                    file.write(node_mnemonic)
                print("* File copying completed, restarting services.")
                # Wipe backup folder and re-create
                timestamp = time.strftime("%Y%m%d-%H%M%S")
                backup_dir = (
                    f"{easy_env_fra.user_home_dir}/findora_backup_{format(timestamp)}"
                )
                shutil.copytree(easy_env_fra.findora_backup, backup_dir)
                shutil.rmtree(easy_env_fra.findora_backup)
                shutil.rmtree(easy_env_fra.migrate_dir)
                backup_folder_check()
                # Restart container
                migration_update()
                print_stars()
                print(
                    "* Migration completed, check option #2 to verify your validator information has updated correctly!"
                )

        else:
            print(
                "* We're sorry, your folder is there but you are missing file(s), please try again after fixing the contents."
                + f"\n* Add the files from your old server into:\n* {easy_env_fra.migrate_dir}/tmp.gen.keypair"
                + f"\n* {easy_env_fra.migrate_dir}/config/priv_validator_key.json\n*"
            )

    else:
        migration_instructions()
    return


def run_container_update(status=False) -> None:
    update_findora_container(status)
    return


def migration_check() -> None:
    file_paths = {}
    if os.path.exists(f"{easy_env_fra.migrate_dir}/tmp.gen.keypair"):
        file_paths["tmp.gen.keypair"] = f"{easy_env_fra.migrate_dir}/tmp.gen.keypair"
    else:
        # No tmp.gen.keypair, we're out.
        return False
    if os.path.exists(f"{easy_env_fra.migrate_dir}/priv_validator_key.json"):
        file_paths[
            "priv_validator_key.json"
        ] = f"{easy_env_fra.migrate_dir}/priv_validator_key.json"
    elif os.path.exists(f"{easy_env_fra.migrate_dir}/config/priv_validator_key.json"):
        file_paths[
            "priv_validator_key.json"
        ] = f"{easy_env_fra.migrate_dir}/config/priv_validator_key.json"
    else:
        # No matches on priv_validator_key.json, we're out.
        return False
    if compare_two_files(
        file_paths["tmp.gen.keypair"],
        f'{easy_env_fra.findora_root}/{environ.get("FRA_NETWORK")}/{environ.get("FRA_NETWORK")}_node.key',
    ):
        # If these are the same, already migrated, don't display
        return False
    if compare_two_files(
        file_paths["priv_validator_key.json"],
        f'{easy_env_fra.findora_root}/{environ.get("FRA_NETWORK")}/tendermint/config/priv_validator_key.json',
    ):
        # If these are the same, already migrated, don't display
        return False
    return True


def print_migrate():
    print(
        f"{Fore.CYAN}* 888 -  Migrate To This Server    - Migrate from another server to this server.{Fore.MAGENTA}"
    )


def backup_folder_check() -> None:
    # check for backup folder
    if os.path.exists(easy_env_fra.findora_backup) is False:
        # No dir = mkdir and backup all files
        os.mkdir(easy_env_fra.findora_backup)
        # add all files
        shutil.copy(
            f'{easy_env_fra.findora_root}/{environ.get("FRA_NETWORK")}/{environ.get("FRA_NETWORK")}_node.key',
            f"{easy_env_fra.findora_backup}/tmp.gen.keypair",
        )
        shutil.copytree(
            f'{easy_env_fra.findora_root}/{environ.get("FRA_NETWORK")}/tendermint/config',
            f"{easy_env_fra.findora_backup}/config",
        )
        return
    else:
        # check for tmp.gen.keypair, backup if missing
        if os.path.exists(f"{easy_env_fra.findora_backup}/tmp.gen.keypair"):
            # found tmp.gen.keypair in backups, compare to live
            if (
                compare_two_files(
                    f"{easy_env_fra.findora_backup}/tmp.gen.keypair",
                    f'{easy_env_fra.findora_root}/{environ.get("FRA_NETWORK")}/{environ.get("FRA_NETWORK")}_node.key',
                )
                is False
            ):
                # If they are the same we're done, if they are false ask to update
                question = ask_yes_no(
                    f"* Your tmp.gen.keypair file in {easy_env_fra.findora_backup} does not match "
                    + f'your {easy_env_fra.findora_root}/{environ.get("FRA_NETWORK")}/{environ.get("FRA_NETWORK")}_node.key.'
                    + f'\n* Do you want to copy the key from {easy_env_fra.findora_root}/{environ.get("FRA_NETWORK")}/{environ.get("FRA_NETWORK")}'
                    + f"_node.key to {easy_env_fra.findora_backup}/tmp.gen.keypair as a backup? (Y/N) "
                )
                if question:
                    # Copy key back
                    os.remove(f"{easy_env_fra.findora_backup}/tmp.gen.keypair")
                    shutil.copy(
                        f'{easy_env_fra.findora_root}/{environ.get("FRA_NETWORK")}/{environ.get("FRA_NETWORK")}_node.key',
                        f"{easy_env_fra.findora_backup}/tmp.gen.keypair",
                    )
        else:
            # Key file didn't exist, back it up
            shutil.copy(
                f'{easy_env_fra.findora_root}/{environ.get("FRA_NETWORK")}/{environ.get("FRA_NETWORK")}_node.key',
                f"{easy_env_fra.findora_backup}/tmp.gen.keypair",
            )
        if os.path.exists(f"{easy_env_fra.findora_backup}/config") and os.path.exists(
            f"{easy_env_fra.findora_backup}/config/priv_validator_key.json"
        ):
            # found config folder & priv_validator_key.json
            if (
                compare_two_files(
                    f"{easy_env_fra.findora_backup}/config/priv_validator_key.json",
                    f'{easy_env_fra.findora_root}/{environ.get("FRA_NETWORK")}/tendermint/config/priv_validator_key.json',
                )
                is False
            ):
                # If they are the same we're done, if they are false ask to update
                question = ask_yes_no(
                    f"* Your file {easy_env_fra.findora_backup}/config/priv_validator_key.json does not match "
                    + f'your {easy_env_fra.findora_root}/{environ.get("FRA_NETWORK")}/tendermint/config/priv_validator_key.json.'
                    + f"\n* Do you want to copy your config folder into {easy_env_fra.findora_backup}/config ? (Y/N) "
                )
                if question:
                    # Copy folder back
                    shutil.rmtree(f"{easy_env_fra.findora_backup}/config")
                    shutil.copytree(
                        f'{easy_env_fra.findora_root}/{environ.get("FRA_NETWORK")}/tendermint/config',
                        f"{easy_env_fra.findora_backup}/config",
                    )
        else:
            # Key file didn't exist, back it up
            shutil.rmtree(f"{easy_env_fra.findora_backup}/config")
            shutil.copytree(
                f'{easy_env_fra.findora_root}/{environ.get("FRA_NETWORK")}/tendermint/config',
                f"{easy_env_fra.findora_backup}/config",
            )


def run_findora_menu() -> None:
    menu_options = {
        0: finish_node,
        1: get_curl_stats,
        2: refresh_fn_stats,
        3: claim_findora_rewards,
        4: pre_send_findora,
        5: set_send_options,
        6: change_validator_info,
        7: update_fn_wallet,
        8: run_container_update,
        9: run_clean_script,
        10: run_ubuntu_updates,
        11: server_disk_check,
        12: all_sys_info,
        13: migration_instructions,
        14: coming_soon,
        15: coming_soon,
        16: coming_soon,
        888: migrate_to_server,
        999: menu_reboot_server,
    }
    # Keep this loop going so when an item ends the menu reloads
    while True:
        load_var_file(easy_env_fra.dotenv_file)
        menu_findora()
        # Pick an option, any option
        value = input("* Enter your option: ")
        # Try/Catch - If it's not a number, goodbye, try again
        try:
            value = int(value)
        except (ValueError, KeyError, TypeError) as e:
            subprocess.run("clear")
            print_stars()
            print(
                f"* {value} is not a valid number, try again. Press enter to continue.\n* Error: {e}"
            )
        # clear before load
        subprocess.run("clear")
        print_stars()
        try:
            menu_options[value]()
        except (ValueError, KeyError, TypeError) as e:
            subprocess.run("clear")
            print_stars()
            print(
                f"* {value} is not a valid number, try again. Press enter to continue.\n* Error: {e}"
            )
        pause_for_cause()


def parse_flags(parser):
    # add the '--verbose' flag
    parser.add_argument(
        "-s",
        "--stats",
        action="store_true",
        help="Run your stats if Findora is installed and running.",
    )

    parser.add_argument(
        "-c",
        "--claim",
        action="store_true",
        help="Claim all of your pending Unclaimed FRA.",
    )

    parser.add_argument(
        "--mainnet", action="store_true", help="Will run the installer set to mainnet."
    )

    parser.add_argument(
        "--testnet", action="store_true", help="Will run the installer set to testnet."
    )

    parser.add_argument(
        "--reset",
        action="store_true",
        help="This will wipe everything to allow you to reload Findora.",
    )

    # parse the arguments
    args = parser.parse_args()

    # Load Vars / Set Network
    first_env_check(easy_env_fra.dotenv_file, easy_env_fra.user_home_dir)

    subprocess.run("clear")
    print(Fore.MAGENTA)

    if args.claim:
        claim_findora_rewards()
        finish_node()

    if args.mainnet:
        if environ.get("FRA_NETWORK"):
            print_stars()
            print(
                f'* You already have {environ.get("FRA_NETWORK")} set in your .easynode.env file\n* If this is a brand new install run --reset first to wipe then try this again.\n*\n* Press enter to load the menu or ctrl+c to quit and restart.'
            )
            print_stars()
            input()
        else:
            set_var(easy_env_fra.dotenv_file, "FRA_NETWORK", "mainnet")
            menu_install_findora(environ.get('FRA_NETWORK'))

    if args.testnet:
        if environ.get("FRA_NETWORK"):
            print_stars()
            print(
                f'* You already have {environ.get("FRA_NETWORK")} set in your .easynode.env file\n* If this is a brand new install run --reset first to wipe then try this again.\n*\n* Press enter to load the menu or ctrl+c to quit and restart.'
            )
            print_stars()
            input()
        else:
            set_var(easy_env_fra.dotenv_file, "FRA_NETWORK", "testnet")
            menu_install_findora(environ.get('FRA_NETWORK'))

    if args.stats:
        menu_topper()
        finish_node()

    if args.reset:
        print_stars()
        answer = ask_yes_no(
            f"* You've started the reset process. Press Y to reset or N ot exit: (Y/N) "
        )
        if answer:
            # wipe data here
            subprocess.call(
                [
                    "wget",
                    "-O",
                    f"/tmp/wipe_findora_{environ.get('FRA_NETWORK')}.sh",
                    f"https://raw.githubusercontent.com/easy-node-pro/findora-validator-scripts/main/wipe_findora_{environ.get('FRA_NETWORK')}.sh",
                ],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            subprocess.call(
                ["bash", "-x", f"/tmp/wipe_findora_{environ.get('FRA_NETWORK')}.sh"],
                cwd=easy_env_fra.user_home_dir,
            )
            finish_node()
