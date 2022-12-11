import subprocess
import os
import dotenv
import shutil
import time
import json
from simple_term_menu import TerminalMenu
from urllib.parse import unquote
from os import environ
from colorama import Fore, Back, Style
from subprocess import PIPE, run
from pprint import pprint
from toolbox.library import (
    print_stars,
    print_stars_reset,
    return_txt,
    load_var_file,
    disk_partitions,
    converted_unit,
    free_space_check,
    all_sys_info,
    ask_yes_no,
    coming_soon,
    run_ubuntu_updater,
    menu_error,
    menu_reboot_server,
    finish_node,
    set_var
)
from config import easy_env_fra

def set_main_or_test() -> None:
    if not environ.get("FRA_NETWORK"):
        subprocess.run("clear")
        print_stars()
        print("* Setup config not found, Does this run on mainnet or testnet?                              *")
        print_stars()
        print("* [0] - Mainnet                                                                             *")
        print("* [1] - Testnet                                                                             *")
        print_stars()
        menu_options = [
            "[0] Mainnet",
            "[1] Testnet",
        ]
        terminal_menu = TerminalMenu(menu_options, title="Mainnet or Testnet")
        results = terminal_menu.show()
        if results == 0:
            set_var(easy_env_fra.dotenv_file, "FRA_NETWORK", "mainnet")
        if results == 1:
            set_var(easy_env_fra.dotenv_file, "FRA_NETWORK", "testnet")
        subprocess.run("clear")
    return

def menu_findora() -> None:
    # menuTopperFull()
    for x in return_txt(easy_env_fra.findora_menu):
        x = x.strip()
        try:
            x = eval(x)
        except SyntaxError:
            pass
        if x:
            print(x)

def refresh_wallet_stats() -> None:
    try:
        output = subprocess.check_output(["curl", "http://localhost:26657/status"])
        output = output.decode()[2:-1]
        data = json.dumps(output, ensure_ascii=False, indent=4)
        # status_code = int(output[1])
        print_stars()
        pprint(data)
    except:
        print("* No response from the rpc.")
    print_stars()
    print("* Press enter to return to the main menu.")
    print_stars()
    input()

def refresh_fn_stats() -> None:
    subprocess.run("clear")
    print_stars()
    try:
        output = unquote(subprocess.check_output(["fn", "show"]))
        print(output)
    except:
        print("* Error, no response from local API, try your curl stats again. If the stats give the same reply try option #10 to get back online and as a last resort option #12!")
    print_stars()
    print("* Press enter to return to the main menu.")
    print_stars()
    input()


def check_balance_menu() -> None:
    print(f"* Coming soon!")
    print_stars()
    input("* Press ENTER to continue.")


def operating_system_updates() -> None:
    print(f"* Coming soon!")
    print_stars()
    input("* Press ENTER to continue.")


def server_disk_check() -> None:
    print_stars_reset()
    print("* Here are all of your mount points: ")
    for part in disk_partitions():
        print(part)
    print_stars()
    total, used, free = shutil.disk_usage(easy_env_fra.our_disk_mount)
    total = str(converted_unit(total))
    used = str(converted_unit(used))
    print(
        "Disk: "
        + str(easy_env_fra.our_disk_mount)
        + "\n"
        + free_space_check(easy_env_fra.our_disk_mount)
        + " Free\n"
        + used
        + " Used\n"
        + total
        + " Total"
    )
    print_stars()
    input("* Disk check complete, press ENTER to return to the main menu. ")

def menu_topper() -> None:
    Load1, Load5, Load15 = os.getloadavg()
    # get sign pct
    # get balances
    # get other validator data
    subprocess.run("clear")
    print_stars()
    print(
        f"{Style.RESET_ALL}{Fore.MAGENTA}* {Fore.MAGENTA}validator-toolbox for Findora FRA Validators by Easy Node   v{easy_env_fra.easy_version}{Style.RESET_ALL}{Fore.MAGENTA}   https://easynode.pro *"
    )
    print_stars()
    print(
        f"* Server Hostname & IP:             {easy_env_fra.server_host_name}{Style.RESET_ALL}{Fore.MAGENTA} - {Fore.YELLOW}{easy_env_fra.our_external_ip}{Style.RESET_ALL}{Fore.MAGENTA}"
    )
    print(
        f"* Current disk space free: {Fore.CYAN}{free_space_check(easy_env_fra.our_disk_mount): >6}{Style.RESET_ALL}{Fore.MAGENTA}\n"
    )
    print_stars()
    print(
        f"* CPU Load Averages: {round(Load1, 2)} over 1 min, {round(Load5, 2)} over 5 min, {round(Load15, 2)} over 15 min"
    )
    print_stars()
    return

def update_findora_container(skip) -> None:
    print(f"* Running the update and restart may cause missed blocks, beware before proceeding!")
    if skip:
        answer = True
    else:
        answer = ask_yes_no(f"* Are you sure you want to check for an upgrade and restart? (Y/N) ")
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
            f"* We will show the output of the upgrade & restart now, this may miss a block(s) depending on your timing."
        )
        subprocess.call(["bash", "-x", f"/tmp/update_{environ.get('FRA_NETWORK')}.sh"], cwd=easy_env_fra.user_home_dir)
        print_stars()
        print(
            f"* Setup has completed. Once you are synced up (catching_up=False) you are ready to create your validator on-chain or migrate from another server onto this server.\n* Press enter to continue."
        )
        print_stars()
        input()
    return

def update_fn_wallet() -> None:
    print(f"* This option upgrades the fn wallet application.")
    answer = ask_yes_no(f"* Do you want to upgrade fn now? (Y/N) ")
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
        print(f"* We will show the output of the upgrade now.")
        subprocess.call(["bash", "-x", f"/tmp/fn_update_{environ.get('FRA_NETWORK')}.sh"], cwd=easy_env_fra.user_home_dir)
        print_stars()
        input("* Fn update complete, press ENTER to return to the main menu. ")
        return

def run_clean_script() -> None:
    print(
        f"* Running the update and restart may cause missed blocks, beware before proceeding!\n* This option runs Safety Clean stopping your container and reloading all data.\n* Run as a last resort in troubleshooting."
    )
    answer = ask_yes_no(f"* Do you want to run safety clean now? (Y/N) ")
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
        print(f"* We will show the output of the reset now.")
        subprocess.call(
            ["bash", "-x", f"/tmp/safety_clean_{environ.get('FRA_NETWORK')}.sh"], cwd=easy_env_fra.user_home_dir
        )
        print_stars()
        input("* Safety clean complete, press ENTER to return to the main menu. ")
        return

def findora_installer() -> None:
    # Run installer ya'll!
    print(
        f"* Welcome to EasyNode.PRO Validator Toolbox for Findora!\n* We've detected that Docker is properly installed for this user, excellent!\n* It doesn't look like you have Findora installed.\n* We will setup Findora validator on this server with a brand new wallet and start syncing with the blockchain."
    )
    answer = ask_yes_no(f"* Do you want to install it now? (Y/N) ")
    if answer:
        # mainnet or testnet
        set_main_or_test()
        subprocess.call(
            [
                "wget",
                f"https://raw.githubusercontent.com/easy-node-pro/findora-validator-scripts/main/easy_install_{environ.get('FRA_NETWORK')}.sh",
                "-O",
                f"/tmp/install_{environ.get('FRA_NETWORK')}.sh",
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        subprocess.run("clear")
        print_stars()
        print(
            f"* We will show the output of the installation, this will take some time to download and unpack.\n* Starting Findora installation now."
        )
        print_stars()
        time.sleep(3)
        print_stars()
        subprocess.call(["bash", "-x", f"/tmp/install_{environ.get('FRA_NETWORK')}.sh"], cwd=easy_env_fra.user_home_dir)
        print_stars()
        print(
            f"* Setup has completed. Once you are synced up (catching_up=False) you are ready to create your validator on-chain or migrate from another server onto this server.\n* Press enter to continue."
        )
        print_stars()
        input()
    else:
        raise SystemExit(0)

def run_ubuntu_updates() -> None:
    question = ask_yes_no(f'* You will miss blocks while upgrades run.\n* Are you sure you want to run updates? (Y/N) ')
    if question:
        subprocess.run("clear")
        print_stars()
        print(f'* Stopping docker container for safety')
        subprocess.call(["docker", "container", "stop", "findorad"])
        run_ubuntu_updater()
        print_stars()
        print(f'* Restarting findorad container')
        subprocess.call(["docker", "container", "start", "findorad"])
        refresh_fn_stats()
    else:
        return

def migrate_to_server() -> None:
    print(f'* Coming soon!')
    return

def run_findora_menu() -> None:
    menu_options = {
        0: finish_node,
        1: refresh_wallet_stats,
        2: refresh_fn_stats,
        3: check_balance_menu,
        4: coming_soon,
        5: coming_soon,
        6: coming_soon,
        7: coming_soon,
        8: coming_soon,
        9: update_fn_wallet,
        10: update_findora_container,
        11: run_ubuntu_updates,
        12: run_clean_script,
        13: server_disk_check,
        14: coming_soon,
        15: all_sys_info,
        888: migrate_to_server,
        999: menu_reboot_server,
    }
    subprocess.run("clear")
    menu_topper()
    menu_findora()
    # Keep this loop going so when an item ends the menu reloads
    while True:
        # Pick an option, any option
        value = input("* Enter your option: ")
        # Try/Catch - If it's not a number, goodbye, try again
        try:
            value = int(value)
        except ValueError:
            subprocess.run("clear")
            print_stars()
            print(f"* {value} is not a number, try again. Press enter to continue.")
            print_stars()
            input()
            run_findora_menu()
        # clear before load
        subprocess.run("clear")
        print_stars()
        # This is so we can bypass
        if value == 10:
            update_findora_container(False)
        else:
            menu_options[value]()
        break
    run_findora_menu()
