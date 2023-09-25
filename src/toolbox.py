import subprocess
import platform
import os
import time
import json
import shutil
import requests
import docker
import dotenv
import psutil
import cmd2
from datetime import datetime, timezone
from simple_term_menu import TerminalMenu
from collections import namedtuple
from datetime import datetime
from os import environ
from dotenv import load_dotenv
from colorama import Fore, Back, Style
from pprint import pprint
from updater import run_update_restart
from safety_clean import run_safety_clean
from shared import ask_yes_no, compare_two_files, create_staker_memo, findora_env

# from shared import stop_and_remove_container
from installer import run_full_installer


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


print_whitespace = print_stuff.printWhitespace
print_stars = print_stuff().printStars
string_stars = print_stuff().stringStars
print_stars_reset = print_stuff(reset=1).printStars
string_stars_reset = print_stuff(reset=1).stringStars


# loader intro splash screen
def loader_intro():
    print_stars()
    p = f"""*
*
* ███████╗██╗███╗   ██╗██████╗  ██████╗ ██████╗  █████╗
* ██╔════╝██║████╗  ██║██╔══██╗██╔═══██╗██╔══██╗██╔══██╗
* █████╗  ██║██╔██╗ ██║██║  ██║██║   ██║██████╔╝███████║
* ██╔══╝  ██║██║╚██╗██║██║  ██║██║   ██║██╔══██╗██╔══██║
* ██║     ██║██║ ╚████║██████╔╝╚██████╔╝██║  ██║██║  ██║
* ╚═╝     ╚═╝╚═╝  ╚═══╝╚═════╝  ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝
*
* ████████╗ ██████╗  ██████╗ ██╗     ██████╗  ██████╗ ██╗  ██╗
* ╚══██╔══╝██╔═══██╗██╔═══██╗██║     ██╔══██╗██╔═══██╗╚██╗██╔╝
*    ██║   ██║   ██║██║   ██║██║     ██████╔╝██║   ██║ ╚███╔╝
*    ██║   ██║   ██║██║   ██║██║     ██╔══██╗██║   ██║ ██╔██╗
*    ██║   ╚██████╔╝╚██████╔╝███████╗██████╔╝╚██████╔╝██╔╝ ██╗
*    ╚═╝    ╚═════╝  ╚═════╝ ╚══════╝╚═════╝  ╚═════╝ ╚═╝  ╚═╝
*
*     Findora Validator Management
*     created by Patrick @ https://EasyNode.pro
*
*"""
    print(p)
    return


def set_var(env_file, key_name, update_name):
    if environ.get(key_name):
        dotenv.unset_key(env_file, key_name)
    dotenv.set_key(env_file, key_name, update_name)
    load_var_file(findora_env.dotenv_file)
    return


def load_var_file(var_file):
    if os.path.exists(var_file):
        load_dotenv(var_file, override=True)
    else:
        subprocess.run(["touch", var_file])


def finish_node():
    print(
        "* Thanks for using Findora Toolbox\n"
        + "* Please consider joining our discord & supporting us one time\n"
        + "* or monthly at https://bit.ly/easynodediscord today!\n*\n* Goodbye!"
    )
    print_stars()
    raise SystemExit(0)


def pause_for_cause():
    print(Fore.MAGENTA)
    print_stars()
    print("* Press enter to return to the main menu.")
    print_stars()
    input()


def check_preflight_setup(env_file, home_dir, USERNAME=findora_env.active_user_name):
    # Check for missing commands we use in the toolbox
    for tool in ["wget", "curl", "pv", "docker"]:
        if subprocess.call(["which", tool], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) != 0:
            print(
                f"{Fore.YELLOW}* The package: {Fore.RED}{tool}{Fore.YELLOW}\n"
                + "* Has not been installed on this system for the user {USERNAME}!\n"
                + "* Install {tool} by running the following command:\n*\n"
                + "* {Fore.CYAN}sudo apt install {tool} -y{Fore.MAGENTA}\n*\n"
                + "* Then re-start the toolbox."
            )
            print_stars()
            print(
                f"* To run all the prerequisites for toolbox in one command, run the following setup code:\n*\n"
                + "* `apt-get update && apt-get upgrade -y && curl -fsSL https://download.docker.com/linux/ubuntu/gpg "
                + '| apt-key add - && add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu focal '
                + 'stable" && apt install apt-transport-https ca-certificates curl pv software-properties-common docker-ce '
                + "docker-ce-cli dnsutils docker-compose containerd.io bind9-dnsutils git python3-pip python3-dotenv unzip "
                + "-y && systemctl start docker && systemctl enable docker && usermod -aG docker servicefindora`\n"
                + "* If you were missing docker, reconnect in a new terminal to gain access on `servicefindora`, then run "
                + "the toolbox again."
            )
            print_stars()
            exit(1)
    # Check if we have a .env file, if not, create it.
    if not os.path.exists(env_file):
        os.system(f"touch {home_dir}/.findora.env")
    else:
        load_var_file(findora_env.dotenv_file)

    # Check if we have a network/region set, if not, ask for it.
    network = set_main_or_test()
    region = set_na_or_eu()
    return network, region


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
    print_stars()
    print(
        "* "
        + Fore.RED
        + "WARNING"
        + Style.RESET_ALL
        + ": Only numbers are possible, please try your selection on the main menu once again."
        + "\n* Press enter to return to the menu."
    )
    print_stars()
    return


def menu_reboot_server() -> str:
    question = ask_yes_no(
        Fore.RED
        + f"* {Fore.RED}WARNING: YOU WILL MISS BLOCKS WHILE YOU REBOOT YOUR ENTIRE SERVER.{Fore.MAGENTA}\n\n"
        + "* Reconnect after a few moments & Run the Validator Toolbox Menu again with: "
        + "python3 ~/findora-toolbox/start.py\n"
        + Fore.WHITE
        + "* We will stop your container safely before restarting\n* Are you sure you would "
        + "like to proceed with rebooting your server? (Y/N) "
    )
    if question:
        print(
            "* Stopping docker container for safety\n* Run toolbox after you reboot to get "
            + "back online or start your container manually with `docker container start findorad`"
            + " when you re-login!"
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
        # Create a Docker client to check if Docker is installed and running
        client = docker.from_env()
        client.ping()
        print("* Docker ready.")
        print_stars()
        time.sleep(1)
    except docker.errors.APIError as e:
        print(f"* Docker API error: {e}")
        exit(2)
    except docker.errors.DockerException:
        print("* There's a problem with your Docker. Are you in the `docker` group?")
        print(
            f"* Add your current user to the docker group with: sudo usermod -aG docker {findora_env.active_user_name}"
        )
        print(
            "* We will halt, make sure running the command `docker` works properly before starting the toolbox again."
        )
        print("* See: https://guides.easynode.pro/admin#docker-installation")
        print_stars()
        finish_node()
        exit(3)
    finally:
        # Close the Docker client
        try:
            client.close()
        except UnboundLocalError:
            pass  # client was not successfully initialized


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


def container_running(container_name: str) -> bool:
    try:
        # Create a Docker client
        client = docker.from_env()

        # List all running containers
        running_containers = client.containers.list()

        # Check if a container with the specified name is in the list of running containers
        return any(container.name == container_name for container in running_containers)
    except docker.errors.APIError as e:
        print(f"* Docker API error: {e}")
        exit(2)
    except docker.errors.DockerException:
        print("* There's a problem with your Docker.")
        print_stars()
        exit(3)
    finally:
        # Close the Docker client
        try:
            client.close()
        except UnboundLocalError:
            pass  # client was not successfully initialized


def ask_question_menu(var_name, question_message, question_title, options_list) -> None:
    menu_options = []
    if environ.get(var_name):
        result = environ.get(var_name)
    else:
        print_stars()
        print(question_message)
        print_stars()
        for option in options_list:
            print(f"* {option}")
            menu_options.append(option)
        print_stars()
        terminal_menu = TerminalMenu(menu_options, title=question_title)
        choice_index = terminal_menu.show()
        result = options_list[choice_index]
        set_var(findora_env.dotenv_file, var_name, result)

    return result


def ask_question_menu_no_var(question_message, question_title, options_list) -> None:
    menu_options = []
    print_stars()
    print(question_message)
    print_stars()
    for option in options_list:
        print(f"* {option}")
        menu_options.append(option)
    print_stars()
    terminal_menu = TerminalMenu(menu_options, title=question_title)
    result = terminal_menu.show()

    return result


def set_na_or_eu() -> None:
    region = ask_question_menu(
        "FRA_REGION",
        "* Setup config not found, Which region should this server download from?",
        "North America or Europe based server?",
        ["na", "eu"],
    )
    return region


def set_main_or_test() -> None:
    network = ask_question_menu(
        "FRA_NETWORK",
        "* Setup config not found, Does this run on mainnet or testnet?                              *",
        "Mainnet or Testnet",
        ["mainnet", "testnet"],
    )
    return network


def menu_findora() -> None:
    print(Fore.MAGENTA)
    update = menu_topper()
    print("* Findora Validator Toolbox - Menu Options:")
    print("*")
    print("*   1 -  Show 'curl' stats info    - Run this to show your local curl stats!")
    print("*   2 -  Show 'fn' stats info      - Run this to show your local fn stats!")
    print("*   3 -  Claim Pending FRA         - Claim all of your unclaimed FRA now")
    print("*   4 -  Transfer FRA              - Send FRA to another fra address now")
    print("*   5 -  Set Transfer Options Menu - Configure your preferred send wallet & privacy")
    print("*   6 -  Change Rate or Info Menu  - Change your rate. Change info coming soon.")
    print("*   7 -  Update fn Application     - Pull update for the wallet application, fn")
    print(f"*                                   {Fore.CYAN}{Back.RED}The Danger Zone:{Style.RESET_ALL}{Fore.MAGENTA}")
    findora_container_update(update)
    print("*   9 -  Run Safety Clean          - Stop your container, reset and download database fresh")
    print("*  10 -  Update Operating System   - Update Ubuntu Operating System Files")
    print(
        f"*                                   {Fore.BLUE}{Back.YELLOW}Informational Section:{Style.RESET_ALL}{Fore.MAGENTA}"
    )
    print("*  11 -  Show system disk info     - Current drive space status")
    print("*  12 -  TMI about your Server     - Seriously a lot of info about this server")
    print("*  13 -  Instructions on Migrating - Run this to read info on migrating to this server.")
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
    print_stars()
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
    print_stars()
    try:
        output = subprocess.check_output(["fn", "show"])
        output = output.decode().replace("b'", "")
        print(output)
    except subprocess.CalledProcessError as err:
        print(
            "* Error, no response from local API, try your command again or "
            + f"check your fn stats to see if there's an issue.\n* Error: {err}"
        )


def claim_findora_rewards() -> None:
    print_stars()
    try:
        output = subprocess.call(
            ["fn", "claim"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        print(f"* Claim all pending completed, refresh your stats after the next block.")
    except subprocess.CalledProcessError as err:
        print(
            "* Error, no response from local API, try your command again or "
            + f"check your fn stats to see if there's an issue.\n* Error: {err}"
        )


def get_total_send(our_fn_stats) -> None:
    # Get fra input and process
    total = input(
        f'* Current balance is: {Fore.GREEN}{our_fn_stats["Balance"]}'
        + f"{Fore.MAGENTA}\n*\n* How much FRA total would you like to send from your validator? "
    )
    total2 = input(f"*\n* Please re-enter the amount of FRA you would like to transfer for verification: ")
    if total == total2:
        return total
    else:
        input("*\n* Balances did not match, try again. Press enter to try again.")
        get_total_send(our_fn_stats)


def get_receiver_address() -> None:
    # IF we've already got it, check it or ask
    if environ.get("RECEIVER_WALLET"):
        question = ask_yes_no(
            f'* We have {Fore.YELLOW}{environ.get("RECEIVER_WALLET")}{Fore.MAGENTA} on file. Would you like to send to '
            + "this address? (Y/N)"
        )
        if question:
            return environ.get("RECEIVER_WALLET")
    address = input(f"*\n* Please input the fra1 address you would like to send your FRA: ")
    if address[:4] != "fra1" or len(address) != 62:
        input(f"* {address} does not look like a valid fra1 address, please retry. Press enter to return to try again.")
        get_receiver_address()
    if address == environ.get("RECEIVER_WALLET"):
        print("* This is already your saved wallet, try again with a new wallet to update this option.")
        return environ.get("RECEIVER_WALLET")
    address2 = input(f"*\n* Please re-input the fra1 address you would like to send your FRA for verification: ")
    if address == address2:
        return address
    else:
        input("* Address did not match, try again. Press enter to try again.")
        get_receiver_address()


def get_privacy_option() -> None:
    # IF we've already got it, check it or ask
    if environ.get("PRIVACY"):
        question = ask_yes_no(
            f'* We have Privacy = {environ.get("PRIVACY")} on file, Would you like to use this option for this transaction '
            + "as well? (Y/N) "
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
    if receiver_address == environ.get("RECEIVER_WALLET") and privacy == environ.get("PRIVACY"):
        return
    # ask and set
    print_stars()
    print(
        f"*\n* Currently used options:\n* Address: {Fore.YELLOW}{receiver_address}"
        + f'{Fore.MAGENTA}\n* Privacy {privacy}\n* Express send: {environ.get("SEND_EXPRESS")}'
    )
    question = ask_yes_no(
        f"*\n* Would you like to save this wallet and privacy setting as default options to "
        + "bypass all these questions next time? (Y/N) "
    )
    if question:
        set_var(findora_env.dotenv_file, "SEND_EXPRESS", "True")
        set_var(findora_env.dotenv_file, "RECEIVER_WALLET", receiver_address)
        set_var(findora_env.dotenv_file, "PRIVACY", f"{privacy}")
    print(
        f"* Currently saved options:\n* Address: {Fore.YELLOW}{receiver_address}{Fore.MAGENTA}"
        + f'\n* Privacy {privacy}\n* Express send: {environ.get("SEND_EXPRESS")}'
    )
    return


def pre_send_findora() -> None:
    # Get balance
    output = fetch_fn_show_output()
    our_fn_stats = get_fn_stats(output)
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
            f"*\n* We are going to send {Fore.GREEN}{send_total}{Fore.MAGENTA} to address {Fore.YELLOW}"
            + f"{receiver_address}{Fore.MAGENTA} with Privacy set to True.\n*\n* "
            + "Press Y to send or N to return to the main menu. (Y/N) "
        )
        if question:
            send_findora(convert_send_total, send_total, receiver_address, "True")
        else:
            return
    else:
        # Send tx regular
        question = ask_yes_no(
            f"*\n* We are going to send {Fore.GREEN}{send_total}{Fore.MAGENTA} to address {Fore.YELLOW}"
            + f"{receiver_address}{Fore.MAGENTA} with Privacy set to False."
            + "\n*\n* Press Y to send or N to return to the main menu. (Y/N) "
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
            f"{Fore.MAGENTA}*\n* Sent {Fore.GREEN}{fra_amount}{Fore.MAGENTA} to {Fore.YELLOW}"
            + f"{to_address}{Fore.MAGENTA} with privacy = {privacy}\n*\n* "
            + "Please note it will take at least a block to get updated stats in toolbox.\n*\n*"
        )
    except subprocess.CalledProcessError as err:
        print(f"{Fore.MAGENTA}* Error sending transaction:\n* {err}\n* Please try again later.")
    return


def change_rate(our_fn_stats):
    print_stars()
    print(f"* Current Rate: {our_fn_stats['Commission Rate']}")
    answer = input(
        "* What would you like the new rate to be?\n* Please use findora notation, "
        + "example for 5% fees use: 0.05\n* Enter your new rate now: "
    )
    answer2 = input("* Please re-enter your new rate to confirm: ")
    if answer == answer2:
        question = ask_yes_no(f"* Are you sure you want to change your rate to {float(answer)*100}%? (Y/N) ")
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
        memo_items = {key: value for key, value in self.our_fn_stats["memo"].items()}
        options = []
        for key, value in memo_items.items():
            options.append(f"{key} - {value}")
        options.append("Exit")
        file_updated = False
        while True:
            print_stars()
            print("* Current Settings: ")
            print_stars()
            choice = self.select(options)
            if choice == "Exit" or choice == "Exit and Send Update":
                if not file_updated:
                    print("* No changes detected, returning to main menu.")
                    return
                else:
                    memo_items_json = json.dumps(memo_items)
                    print("* Here is your updated staker_memo information for verification before sending changes:")
                    print_stars()
                    print(memo_items)
                    print_stars()
                    question = ask_yes_no(
                        "* Do you want to update ~/staker_memo with these changes and send on chain update now? (Y/N) "
                    )
                    if question:
                        with open(findora_env.staker_memo_path, "w") as file:
                            file.write(memo_items_json)
                        subprocess.call(["fn", "staker-update", "-M", memo_items_json])
                        print(Fore.MAGENTA)
                        print_stars()
                        print(
                            f"* Blockchain update completed, please wait at least 1 block before checking for updated "
                            + "information."
                        )
                    print_stars()
                    return
            file_updated = True
            key = choice.split(" - ")[0]
            new_value = input("Enter the new value: ")
            memo_items[key] = new_value
            options[options.index(choice)] = f"{key} - {new_value}"
            options[-1] = "Exit and Send Update"


class MemoUpdaterLocalFiles(cmd2.Cmd):
    def __init__(self, staker_memo_path):
        super().__init__()
        self.staker_memo_path = staker_memo_path
        # Load the staker_memo data from the file
        if os.path.exists(staker_memo_path):
            with open(staker_memo_path, 'r') as file:
                self.memo_items = json.load(file)
        else:
            print(f"Error: The file {staker_memo_path} does not exist.")
            self.memo_items = {}

    def do_update(self, arg):
        options = []
        for key, value in self.memo_items.items():
            options.append(f"{key} - {value}")
        options.append("Exit")
        file_updated = False
        while True:
            print_stars()
            print("* Current Settings: ")
            print_stars()
            choice = self.select(options)
            if choice == "Exit" or choice == "Exit and Send Update":
                if not file_updated:
                    print("* No changes detected, returning to main menu.")
                    return
                else:
                    memo_items_json = json.dumps(self.memo_items)
                    print("* Here is your updated staker_memo information for verification before sending changes:")
                    print_stars()
                    print(self.memo_items)
                    print_stars()
                    question = ask_yes_no(
                        "* Do you want to update ~/staker_memo with these changes and send on chain update now? (Y/N) "
                    )
                    if question:
                        with open(self.staker_memo_path, "w") as file:
                            file.write(memo_items_json)
                        subprocess.call(["fn", "staker-update", "-M", memo_items_json])
                        print(Fore.MAGENTA)
                        print_stars()
                        print(
                            f"* Blockchain update completed, please wait at least 1 block before checking for updated "
                            + "information."
                        )
                    print_stars()
                    return
            file_updated = True
            key = choice.split(" - ")[0]
            new_value = input("Enter the new value: ")
            self.memo_items[key] = new_value
            options[options.index(choice)] = f"{key} - {new_value}"
            options[-1] = "Exit and Send Update"

def change_validator_info():
    print_stars()
    output = fetch_fn_show_output()
    our_fn_stats = get_fn_stats(output)
    if "Self Delegation" not in our_fn_stats:
        print(
            "* You have not created your validator yet. Please exit, stake with your validator "
            + "wallet and send the create validator command.\n* See our post install guide "
            + "at https://guides.easynode.pro/findora/post#validator-wallet-commands"
            + "\n*\n* Press enter to return to the main menu."
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
    terminal_menu = TerminalMenu(change_info_menu, title="* What would you like to update today? ")
    response = terminal_menu.show()
    # add logic for choices here pass our_fn_stats to #2
    if response == 0:
        change_rate(our_fn_stats)
        return
    if response == 1:
        # Initialize and run
        updater = MemoUpdater(our_fn_stats)
        # allow edit one by one, then have commit changes at the end?
        updater.do_update(None)
        return
    if response == 2:
        return
    return


def check_address_input(address) -> None:
    if address[:4] != "fra1" or len(address) != 62:
        input(f"* {address} does not look like a valid fra1 address, please retry. Press enter to return to the menu.")
        return
    if address == environ.get("RECEIVER_WALLET"):
        input(
            "* This is already your saved wallet, try again with a new wallet to update this option. Press enter to return "
            + "to the menu."
        )
        return
    address2 = input(f"*\n* Please re-input the fra1 address you would like to send your FRA for verification: ")
    if address == address2:
        set_var(findora_env.dotenv_file, "RECEIVER_WALLET", address)
        input(f"* Wallet updated to {Fore.YELLOW}{address}{Fore.MAGENTA}")
        return
    else:
        input("* Address did not match, try again with matching info. Press enter to return to the menu.")
        return


def set_send_options() -> None:
    # Give'm some options!
    print(Fore.MAGENTA)
    print_stars()
    menu_option = ask_question_menu_no_var(
        f"* Select a send tx option to change: \n*\n* 0. Express Wallet - Currently {Fore.YELLOW}"
        + f"{environ.get('RECEIVER_WALLET')}{Fore.MAGENTA}\n* 1. Privacy Option - Change current "
        + f"privacy option: {environ.get('PRIVACY')}\n* 2. Express Option - Change current "
        + f"express option: {environ.get('SEND_EXPRESS')}\n* 3. Exit - Return to Main Menu\n*",
        "* Which option would you like to update?",
        ["Set Wallet", "Set Privacy", "Set Express", "Exit to Main Menu"],
    )
    if menu_option == 0:
        address = input(f"*\n* Please input the fra1 address you would like to send your FRA: ")
        check_address_input(address)
    if menu_option == 1:
        ask_question_menu(
            "PRIVACY",
            "* Would you like private transactions? ",
            f'* Privacy option currently set to {environ.get("PRIVACY", "none")}. Would you like to switch this?',
            ["True", "False"],
        )
    if menu_option == 2:
        ask_question_menu(
            "SEND_EXPRESS",
            "* Would you like private transactions? ",
            f'* Express option currently set to {environ.get("SEND_EXPRESS", "none")}. Would you like to switch this?',
            ["True", "False"],
        )
    if menu_option == 3:
        return
    set_send_options()


def server_disk_check() -> None:
    print_stars_reset()
    print("* Here are all of your mount points: ")
    for part in disk_partitions():
        print(part)
    print_stars()
    total, used, free = shutil.disk_usage(findora_env.findora_root)
    total = str(converted_unit(total))
    used = str(converted_unit(used))
    print(
        "Disk: "
        + str(findora_env.findora_root)
        + "\n"
        + free_space_check(findora_env.findora_root)
        + " Free\n"
        + used
        + " Used\n"
        + total
        + " Total"
    )


def get_container_version(url="http://localhost:8668/version") -> None:
    response = requests.get(url)
    return response.text


def findora_container_update(update) -> None:
    if update:
        print(
            f"{Fore.CYAN}*   8 -  Update Findora Container  - Pull & Restart the latest container from Findora{Fore.MAGENTA}"
        )
        return
    else:
        print("*   8 -  Update Findora Container  - Pull & Restart the latest container from Findora")
        return


def findora_gwei_convert(findora):
    fra_amount = int(findora) / 1000000
    return fra_amount


def extract_json_section(output, section_name):
    """
    Further improved version to extract the JSON sections.
    """
    start_tag = section_name + ":"

    start_index = output.find(start_tag)
    if start_index == -1:
        return None

    # Move the start_index to the start of the JSON data
    start_index += len(start_tag)

    brace_count = 0
    for i, char in enumerate(output[start_index:]):
        if char == "{":
            brace_count += 1
        elif char == "}":
            brace_count -= 1
            if brace_count == 0:
                end_index = i + start_index + 1
                break

    json_data = output[start_index:end_index].strip()

    try:
        return json.loads(json_data)
    except json.JSONDecodeError:
        return None


def extract_value(output, key):
    """
    Refined version of extract_value to handle various cases of value placements.
    """
    lines = output.split("\n")
    for i, line in enumerate(lines):
        if key in line:
            # If the line contains a colon, but no value after the colon
            if ":" in line and len(line.split(":")[1].strip()) == 0:
                # Check the next line for the value
                if i + 1 < len(lines) and "{" not in lines[i + 1]:
                    return lines[i + 1].strip()
                # If the next line isn't the value, check two lines below for the value
                elif i + 2 < len(lines):
                    return lines[i + 2].strip()
            # If the line contains a colon, extract the value after the colon
            elif ":" in line:
                return line.split(":")[1].strip()
    return None


def fetch_fn_show_output():
    """
    Executes the 'fn show' command, processes its output, and returns the cleaned up output.
    """
    try:
        output = subprocess.check_output(["fn", "show"])
        cleaned_output = output.decode().replace("b'", "").replace("\x1b[31;01m", "").replace("\x1b[00m", "")
        return cleaned_output
    except subprocess.CalledProcessError:
        # Handle any errors that might occur during command execution.
        return ""


def get_fn_stats(output):
    # Parse JSON sections
    delegation_info = extract_json_section(output, "Your Delegation")
    staking_info = extract_json_section(output, "Your Staking")

    # Extract other values
    network = extract_value(output, "Server URL")
    balance_raw = extract_value(output, "Node Balance")
    balance = f"{findora_gwei_convert(int(balance_raw.split()[0])):,.2f}" if balance_raw else "0"

    # Create the result dictionary with default values
    fn_info = {
        "Network": network,
        "Balance": balance,
        "Pending Rewards": "0.00",
        "Self Delegation": "0.00",
        "Current Block": "N/A",
        "Proposed Blocks": "0",
        "Pending Pool Rewards": "0.00",
        "Server Rank": "N/A",
        "Delegator Count": "N/A",
        "Commission Rate": "0.00%",
        "memo": {"name": "N/A", "desc": "N/A", "website": "N/A", "logo": "N/A"},
    }

    # Extract delegation details
    if delegation_info:
        bond = delegation_info.get("bond", 0)
        fn_info["Self Delegation"] = f"{findora_gwei_convert(bond):,.2f}"

        current_block = delegation_info.get("current_height", 0)
        fn_info["Current Block"] = str(current_block)

        your_delegation_rewards = delegation_info.get("rewards", 0)
        fn_info["Pending Rewards"] = f"{findora_gwei_convert(your_delegation_rewards):,.2f}"

    # Extract staking details (if available)
    if staking_info:
        proposed_blocks = staking_info.get("block_proposed_cnt", 0)
        fn_info["Proposed Blocks"] = str(proposed_blocks)

        unclaimed_rewards = staking_info.get("fra_rewards", 0)
        fn_info["Pending Pool Rewards"] = f"{findora_gwei_convert(unclaimed_rewards):,.2f}"

        server_rank = staking_info.get("voting_power_rank")
        fn_info["Server Rank"] = str(server_rank) if server_rank is not None else "N/A"

        delegator_count = staking_info.get("delegator_cnt")
        fn_info["Delegator Count"] = str(delegator_count) if delegator_count is not None else "N/A"

        commission_rate = staking_info.get("commission_rate", [0, 1])
        commission_percentage = (commission_rate[0] / commission_rate[1]) * 100
        fn_info["Commission Rate"] = f"{commission_percentage:.2f}%"

        memo = staking_info.get("memo", {})
        fn_info["memo"] = {
            "name": memo.get("name", "N/A"),
            "desc": memo.get("desc", "N/A"),
            "website": memo.get("website", "N/A"),
            "logo": memo.get("logo", "N/A"),
        }

    return fn_info


def menu_topper() -> None:
    try:
        Load1, Load5, Load15 = os.getloadavg()
        curl_stats = capture_stats()
        now = datetime.now(timezone.utc)
        fra = findora_gwei_convert(curl_stats["result"]["validator_info"]["voting_power"])
        our_version = get_container_version()
        output = fetch_fn_show_output()
        our_fn_stats = get_fn_stats(output)
        external_ip = findora_env.our_external_ip
        try:
            our_fn_stats.pop("memo")
        except KeyError as err:
            pass
        online_version = get_container_version(
            f'https://{findora_env.fra_env}-{environ.get("FRA_NETWORK")}.{findora_env.fra_env}.findora.org:8668/version'
        )
    except TimeoutError as e:
        our_version = "No Response"
        online_version = "No Response"
        external_ip = "0.0.0.0"
        print_stars()
        print(f"* Timeout error: {e}")
        print_stars()
        input()

    print(Fore.MAGENTA)
    print_stars()
    print(
        f"{Style.RESET_ALL}{Fore.MAGENTA}* {Fore.MAGENTA}Findora Toolbox Management Menu"
        + f"                 v{findora_env.toolbox_version}{Style.RESET_ALL}{Fore.MAGENTA}   https://findora.org *"
    )
    print_stars()
    print(
        f"* Server Hostname & IP:      {findora_env.server_host_name}{Style.RESET_ALL}{Fore.MAGENTA}"
        + f" - {Fore.YELLOW}{external_ip}{Style.RESET_ALL}{Fore.MAGENTA}"
    )
    print(f"* Public Address:            {curl_stats['result']['validator_info']['address']}")
    if our_fn_stats["Network"] == "https://prod-mainnet.prod.findora.org":
        print(f"* Network:                   Mainnet")
    if our_fn_stats["Network"] == "https://prod-testnet.prod.findora.org":
        print(f"* Network:                   Testnet")
    our_fn_stats.pop("Network")
    print(f"* Current FRA Staked:        {Fore.CYAN}{'{:,}'.format(round(fra, 2))}{Fore.MAGENTA} FRA")
    if curl_stats["result"]["sync_info"]["catching_up"] == "False":
        print(
            f"* Catching Up:                    {Fore.RED}{curl_stats['result']['sync_info']['catching_up']}{Fore.MAGENTA}"
        )
    else:
        print(
            f"* Catching Up:               {Fore.GREEN}{curl_stats['result']['sync_info']['catching_up']}{Fore.MAGENTA}"
        )
    print(
        f"* Local Latest Block:        {curl_stats['result']['sync_info']['latest_block_height']}  * Remote Latest Block:        "
        + f"{our_fn_stats['Current Block']}"
    )
    our_fn_stats.pop("Current Block")
    print(f"* Proposed Blocks:           {our_fn_stats['Proposed Blocks']}")
    our_fn_stats.pop("Proposed Blocks")
    for i in our_fn_stats:
        spaces = "                         "
        print(f"* {i}: {spaces[len(i):]}{our_fn_stats[i]}")
    print(f"* Latest Block Time:         {curl_stats['result']['sync_info']['latest_block_time'][:-11]}")
    print(f"* Current Time UTC:          {now.strftime('%Y-%m-%dT%H:%M:%S')}")
    print(
        f"* Current Disk Space Free:   {Fore.BLUE}{free_space_check(findora_env.findora_root): >6}{Style.RESET_ALL}{Fore.MAGENTA}"
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
        2: run_update_launcher,
        3: run_safety_clean_launcher,
    }
    print(
        "* We still don't detect a running container.\n* Sometimes it can take a few minutes before the api starts responding.\n"
        + "* You can attempt to get stats again for a few minutes, if that doesn't work review docker logs & try the "
        + "update_version.\n* Here are your options currently:"
        + "\n* 1 - CURL stats - Keep checking stats"
        + "\n* 2 - update_version script - Run the update version script as a first option for recovery."
        + "\n* 3 - safety_clean script - Run the safety_clean script as a last option to reset database data and restart server."
        + "\n* 0 - Exit and manually troubleshoot"
    )
    print_stars()
    try:
        option = int(input("Enter your option: "))
    except ValueError:
        menu_error()
        rescue_menu()

    menu_options[option]()
    rescue_menu()


def migration_update() -> None:
    subprocess.call(
        ["bash", "-x", f"{findora_env.toolbox_location}/src/bin/update_{environ.get('FRA_NETWORK')}.sh"],
        cwd=findora_env.user_home_dir,
    )


def update_fn_wallet() -> None:
    print("* This option upgrades the fn wallet application.")
    answer = ask_yes_no("* Do you want to upgrade fn now? (Y/N) ")
    if answer:
        print("* We will show the output of the upgrade now.")
        subprocess.call(
            ["bash", "-x", f"{findora_env.toolbox_location}/src/bin/fn_update_{environ.get('FRA_NETWORK')}.sh"],
            cwd=findora_env.user_home_dir,
        )


def menu_install_findora(network, region) -> None:
    # Run installer ya'll!
    print(
        "* We've detected that Docker is properly installed for this user, excellent!"
        + f"\n* But...it doesn't look like you have Findora {network} installed."
        + "\n* We will setup Findora validator software on this server with a temporary key and wallet file."
        + "\n* After installation finishes, wait for the blockchain to sync before you create a validator or start a migration."
        + "\n* Read more about migrating an existing validator here: "
        + "https://docs.easynode.pro/findora/moving#migrate-your-server-via-validator-toolbox"
    )
    answer = ask_yes_no(
        f"* {Fore.RED}Do you want to install {Fore.YELLOW}{network}{Fore.RED} from the {Fore.YELLOW}{region}{Fore.RED} "
        + f"region now? (Y/N){Fore.MAGENTA} "
    )
    if answer:
        run_full_installer(network, region)
    else:
        raise SystemExit(0)


def run_ubuntu_updates() -> None:
    question = ask_yes_no(
        f"* {Fore.RED}You will miss blocks while upgrades run.\n{Fore.MAGENTA}*{Fore.RED} Are you sure you want to run "
        + f"updates? (Y/N){Fore.MAGENTA} "
    )
    if question:
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


def migration_instructions():
    # path doesn't exist, explain migration process.
    print(
        f"* We didn't locate a folder at {findora_env.migrate_dir}\n*\n* Exit the toolbox, then:"
        + f"\n* 1. Make a folder named {findora_env.migrate_dir}\n* 2. Add your tmp.gen.keypair file into the folder"
        + "\n* 3. Add your config folder containing your priv_validator_key.json file into ~/migrate"
        + "\n* 4. If this server is catching_up=False, you can shut off the old server and relaunch the menu here to migrate."
        + "\n*\n* The goal is to avoid double signing and a 5% slashing fee!!!\n*\n* Load your files and run this "
        + "option again!"
    )


def migrate_to_server() -> None:
    if os.path.exists(f"{findora_env.migrate_dir}"):
        # check for tmp.gen.keypair and priv_validator_key.json in ~/migrate
        print("* You have a migrate folder, checking for files.")
        if (
            os.path.exists(f"{findora_env.migrate_dir}/tmp.gen.keypair")
            and os.path.exists(f"{findora_env.migrate_dir}/config/priv_validator_key.json")
            or os.path.exists(f"{findora_env.migrate_dir}/priv_validator_key.json")
        ):
            print(
                f"* {findora_env.migrate_dir}/tmp.gen.keypair found!\n"
                + f"* {findora_env.migrate_dir}/config/priv_validator_key.json found!"
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
                    f'{findora_env.findora_root}/{environ.get("FRA_NETWORK")}/{environ.get("FRA_NETWORK")}_node.key'
                ):
                    os.remove(
                        f'{findora_env.findora_root}/{environ.get("FRA_NETWORK")}/{environ.get("FRA_NETWORK")}_node.key'
                    )
                shutil.move(
                    f"{findora_env.migrate_dir}/tmp.gen.keypair",
                    f'{findora_env.findora_root}/{environ.get("FRA_NETWORK")}/{environ.get("FRA_NETWORK")}_node.key',
                )
                os.remove(
                    f'{findora_env.findora_root}/{environ.get("FRA_NETWORK")}/tendermint/config/priv_validator_key.json'
                )
                if os.path.exists(f"{findora_env.migrate_dir}/priv_validator_key.json"):
                    shutil.move(
                        f"{findora_env.migrate_dir}/priv_validator_key.json",
                        f'{findora_env.findora_root}/{environ.get("FRA_NETWORK")}/tendermint/config/priv_validator_key.json',
                    )
                elif os.path.exists(f"{findora_env.migrate_dir}/config/priv_validator_key.json"):
                    shutil.move(
                        f"{findora_env.migrate_dir}/config/priv_validator_key.json",
                        f'{findora_env.findora_root}/{environ.get("FRA_NETWORK")}/tendermint/config/priv_validator_key.json',
                    )
                else:
                    print(
                        "* Welp, somehow we didn't find a priv_validator_key.json to migrate."
                        + "\n* You'll have to get your key into the config folder and run a safety clean."
                    )
                node_mnemonic = subprocess.getoutput(
                    f"cat {findora_env.findora_root}/{environ.get('FRA_NETWORK')}/{environ.get('FRA_NETWORK')}_node.key "
                    + "| grep 'Mnemonic' | sed 's/^.*Mnemonic:[^ ]* //'"
                )
                os.remove(f"{findora_env.findora_root}/{environ.get('FRA_NETWORK')}/node.mnemonic")
                subprocess.call(
                    [
                        "touch",
                        f"{findora_env.findora_root}/{environ.get('FRA_NETWORK')}/node.mnemonic",
                    ]
                )
                with open(
                    f"{findora_env.findora_root}/{environ.get('FRA_NETWORK')}/node.mnemonic",
                    "w",
                ) as file:
                    file.write(node_mnemonic)
                print("* File copying completed, restarting services.")
                # Wipe backup folder and re-create
                timestamp = time.strftime("%Y%m%d-%H%M%S")
                backup_dir = f"{findora_env.user_home_dir}/findora_backup_{format(timestamp)}"
                shutil.copytree(findora_env.findora_backup, backup_dir)
                shutil.rmtree(findora_env.findora_backup)
                shutil.rmtree(findora_env.migrate_dir)
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
                + f"\n* Add the files from your old server into:\n* {findora_env.migrate_dir}/tmp.gen.keypair"
                + f"\n* {findora_env.migrate_dir}/config/priv_validator_key.json\n*"
            )

    else:
        migration_instructions()
    return


def migration_check() -> None:
    file_paths = {}
    if os.path.exists(f"{findora_env.migrate_dir}/tmp.gen.keypair"):
        file_paths["tmp.gen.keypair"] = f"{findora_env.migrate_dir}/tmp.gen.keypair"
    else:
        # No tmp.gen.keypair, we're out.
        return False
    if os.path.exists(f"{findora_env.migrate_dir}/priv_validator_key.json"):
        file_paths["priv_validator_key.json"] = f"{findora_env.migrate_dir}/priv_validator_key.json"
    elif os.path.exists(f"{findora_env.migrate_dir}/config/priv_validator_key.json"):
        file_paths["priv_validator_key.json"] = f"{findora_env.migrate_dir}/config/priv_validator_key.json"
    else:
        # No matches on priv_validator_key.json, we're out.
        return False
    if compare_two_files(
        file_paths["tmp.gen.keypair"],
        f'{findora_env.findora_root}/{environ.get("FRA_NETWORK")}/{environ.get("FRA_NETWORK")}_node.key',
    ):
        # If these are the same, already migrated, don't display
        return False
    if compare_two_files(
        file_paths["priv_validator_key.json"],
        f'{findora_env.findora_root}/{environ.get("FRA_NETWORK")}/tendermint/config/priv_validator_key.json',
    ):
        # If these are the same, already migrated, don't display
        return False
    return True


def print_migrate():
    print(f"{Fore.CYAN}* 888 -  Migrate To This Server    - Migrate from another server to this server.{Fore.MAGENTA}")


def backup_folder_check() -> None:
    # check for backup folder
    if os.path.exists(findora_env.findora_backup) is False:
        # No dir = mkdir and backup all files
        os.mkdir(findora_env.findora_backup)
        # add all files
        shutil.copy(
            f'{findora_env.findora_root}/{environ.get("FRA_NETWORK")}/{environ.get("FRA_NETWORK")}_node.key',
            f"{findora_env.findora_backup}/tmp.gen.keypair",
        )
        shutil.copytree(
            f'{findora_env.findora_root}/{environ.get("FRA_NETWORK")}/tendermint/config',
            f"{findora_env.findora_backup}/config",
        )
        return
    else:
        # check for tmp.gen.keypair, backup if missing
        if os.path.exists(f"{findora_env.findora_backup}/tmp.gen.keypair"):
            # found tmp.gen.keypair in backups, compare to live
            if (
                compare_two_files(
                    f"{findora_env.findora_backup}/tmp.gen.keypair",
                    f'{findora_env.findora_root}/{environ.get("FRA_NETWORK")}/{environ.get("FRA_NETWORK")}_node.key',
                )
                is False
            ):
                # If they are the same we're done, if they are false ask to update
                question = ask_yes_no(
                    f"* Your file {findora_env.findora_backup}/tmp.gen.keypair does not match "
                    + f'your live {environ.get("FRA_NETWORK")}_node.key.'
                    + f"\n* Do you want to copy the live key into the {findora_env.findora_backup} folder now? (Y/N) "
                )
                if question:
                    # Copy key back
                    os.remove(f"{findora_env.findora_backup}/tmp.gen.keypair")
                    shutil.copy(
                        f'{findora_env.findora_root}/{environ.get("FRA_NETWORK")}/{environ.get("FRA_NETWORK")}_node.key',
                        f"{findora_env.findora_backup}/tmp.gen.keypair",
                    )
        else:
            # Key file didn't exist, back it up
            shutil.copy(
                f'{findora_env.findora_root}/{environ.get("FRA_NETWORK")}/{environ.get("FRA_NETWORK")}_node.key',
                f"{findora_env.findora_backup}/tmp.gen.keypair",
            )
        if os.path.exists(f"{findora_env.findora_backup}/config") and os.path.exists(
            f"{findora_env.findora_backup}/config/priv_validator_key.json"
        ):
            # found config folder & priv_validator_key.json
            if (
                compare_two_files(
                    f"{findora_env.findora_backup}/config/priv_validator_key.json",
                    f'{findora_env.findora_root}/{environ.get("FRA_NETWORK")}/tendermint/config/priv_validator_key.json',
                )
                is False
            ):
                # If they are the same we're done, if they are false ask to update
                question = ask_yes_no(
                    f"* Your file {findora_env.findora_backup}/config/priv_validator_key.json does not match "
                    + f'your {findora_env.findora_root}/{environ.get("FRA_NETWORK")}/tendermint/config/priv_validator_key.json.'
                    + f"\n* Do you want to copy your config folder into {findora_env.findora_backup}/config ? (Y/N) "
                )
                if question:
                    # Copy folder back
                    shutil.rmtree(f"{findora_env.findora_backup}/config")
                    shutil.copytree(
                        f'{findora_env.findora_root}/{environ.get("FRA_NETWORK")}/tendermint/config',
                        f"{findora_env.findora_backup}/config",
                    )
        else:
            # Key file didn't exist, back it up
            shutil.rmtree(f"{findora_env.findora_backup}/config")
            shutil.copytree(
                f'{findora_env.findora_root}/{environ.get("FRA_NETWORK")}/tendermint/config',
                f"{findora_env.findora_backup}/config",
            )


def run_update_launcher() -> None:
    question = ask_yes_no(
        "* You may miss blocks while restarting the container.\n* Are you sure you want to run the upgrade/restart script? (Y/N) "
    )
    print_stars()
    if question:
        run_update_restart(os.environ.get("FRA_NETWORK"))


def run_safety_clean_launcher() -> None:
    question = ask_yes_no(
        f"* {Fore.RED}You will miss blocks while downloading the new database, this can take awhile depending on location "
        + f"and connection.{Fore.MAGENTA}\n* Are you sure you want to run a safety_clean? (Y/N) "
    )
    print_stars()
    if question:
        run_safety_clean(os.environ.get("FRA_NETWORK"), os.environ.get("FRA_REGION"))


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
        8: run_update_launcher,
        9: run_safety_clean_launcher,
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
        load_var_file(findora_env.dotenv_file)
        menu_findora()
        # Pick an option, any option
        value = input("* Enter your option: ")
        # Try/Catch - If it's not a number, goodbye, try again
        if value == "":
            run_findora_menu()
        try:
            value = int(value)
        except (ValueError, KeyError, TypeError) as e:
            print_stars()
            print(f"* {value} is not a valid number, try again. Press enter to continue.\n* Error: {e}")
        # clear before load

        print_stars()
        try:
            menu_options[value]()
        except (ValueError, KeyError, TypeError) as e:
            print_stars()
            print(f"* {value} is not a valid number, try again. Press enter to continue.\n* Error: {e}")
        pause_for_cause()


def parse_flags(parser, region, network):
    # Add the arguments
    parser.add_argument(
        "-u", "--update", action="store_true", help="Will update and/or restart your Findora container."
    )

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
        "--rescue",
        action="store_true",
        help="Will run the rescue menu with full options, if your container is not running.",
    )

    parser.add_argument(
        "--clean", action="store_true", help="Will run the clean script, removes database, reloads all data."
    )

    parser.add_argument(
        "--fn", action="store_true", help="Will reset fn to your current key files replacing the running ones."
    )

    parser.add_argument(
        "--installer", action="store_true", help="Will run the toolbox installer setup for mainnet or testnet."
    )

    parser.add_argument(
        "--register",
        action="store_true",
        help="Will register your validator on chain after server is synced and deposit is made.",
    )

    parser.add_argument(
        "--ultrareset",
        action="store_true",
        help="WARNING: This will remove all data on your server, make sure you have backups of all key files and data.",
    )

    # parse the arguments
    args = parser.parse_args()

    if args.claim:
        claim_findora_rewards()
        finish_node()

    if args.installer:
        menu_install_findora(network, region)

    if args.fn:
        update_fn_wallet()

    if args.rescue:
        if container_running(findora_env.container_name):
            print_stars()
            question = ask_yes_no("* Your container is running. Are you sure you want to load the rescue menu? (Y/N) ")
            print_stars()
            if question:
                rescue_menu()
            else:
                finish_node()
        else:
            rescue_menu()

    if args.update:
        if container_running(findora_env.container_name):
            print_stars()
            question = ask_yes_no(
                "* Your container is running. Are you sure you want to run the upgrade_script? (Y/N) "
            )
            print_stars()
            if question:
                run_update_restart(os.environ.get("FRA_NETWORK"))
            else:
                finish_node()
        else:
            run_update_restart(os.environ.get("FRA_NETWORK"))

    if args.clean:
        if container_running(findora_env.container_name):
            print_stars()
            question = ask_yes_no(
                "* Your container is running. Are you sure you want to run the safety_clean script? (Y/N) "
            )
            print_stars()
            if question:
                run_safety_clean_launcher()
            else:
                finish_node()
        else:
            run_safety_clean_launcher()

    if args.stats:
        menu_topper()
        finish_node()

    if args.register:
        run_register_node()

    if args.ultrareset:
        # Are you really really sure?
        answer = ask_yes_no(
            f"* WARNING, NUCLEAR OPTION: We will now totally remove all files in /data/findora and beyond.\n* YOU WILL LOSE ALL OF YOUR KEYS AND DATA IN /data/findora\n* After this completes you will need to re-run the installer and wait for a fresh download. Then you will be able to run our migration process.\n* {Fore.RED}Press Y to fully wipe and reset your server or N to exit: (Y/N){Fore.MAGENTA} "
        )
        if answer:
            # wipe data here
            subprocess.call(
                ["bash", "-x", f"{findora_env.toolbox_location}/src/bin/wipe_findora_{environ.get('FRA_NETWORK')}.sh"],
                cwd=findora_env.user_home_dir,
            )
        finish_node()


def run_troubleshooting_process():
    print(f"* Docker is running and working but the container '{findora_env.container_name}' is not.")
    while True:
        answer = ask_yes_no(
            "* Would you like to attempt to run the update_version script to try to get your container back online? (Y/N)"
        )
        if answer:
            run_update_restart(os.environ.get("FRA_NETWORK"))
            break
        else:
            answer2 = ask_yes_no(
                "* Would you like to load the rescue menu to try and troubleshoot (Select N to exit and manually troubleshoot)? (Y/N) "
            )
            if answer2:
                rescue_menu()
            else:
                print(
                    "* Stopping toolbox so you can troubleshoot the container manually.\n"
                    + "* Here's what we suggest in order to try to troubleshoot:\n\n* 1 - Check docker logs for errors with: docker logs findorad\n"
                    + "* 2 - Restart the toolbox with the -u flag to run the upgrade_script: ./findora.sh -u\n"
                    + "* If the above does not work you should be prompted to run a safety clean or you can do that manually with: ./findora.sh --clean\n"
                    + "* If you are still having issues please reach out on our Discord: https://bit.ly/easynodediscord\n"
                )
                print_stars()
                finish_node()

def run_register_node() -> None:
    create_staker_memo()
    output = fetch_fn_show_output()
    our_fn_stats = get_fn_stats(output)
    try:
        our_fn_stats.pop("memo")
    except KeyError as err:
        pass
    balance = float(our_fn_stats["Balance"])
    remaining = 10000 - balance
    for i in our_fn_stats:
        spaces = "                         "
        print(f"* {i}: {spaces[len(i):]}{our_fn_stats[i]}")
    print_stars()
    if balance < 10000:
        print(f"* Not enough FRA to start a validator, please deposit {remaining}+ FRA to continue.\n* Current balance: {balance} FRA")
    else:
        answer = ask_yes_no(f"* You have {balance} FRA, would you like to register & create your validator now? (Y/N) ")
        if answer:
            updater = MemoUpdaterLocalFiles(findora_env.staker_memo_path)
            # allow edit one by one, then have commit changes at the end?
            updater.do_update(None)
            # Validate info
            # Register
            coming_soon()
    print_stars()
    finish_node()
