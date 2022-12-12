import subprocess
import os
import shutil
import time
import json
import shutil
import pwd
import getpass
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
    set_var,
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
    menu_topper()
    for x in return_txt(easy_env_fra.findora_menu):
        x = x.strip()
        try:
            x = eval(x)
        except SyntaxError:
            pass
        if x:
            print(x)

def refresh_wallet_stats() -> None:
    subprocess.run("clear")
    print_stars()
    print(Fore.GREEN)
    try:
        output = subprocess.check_output(["curl", "http://localhost:26657/status"])
        output = output.decode().replace("b'", "")
        output = json.loads(output)
        pprint(output)
    except:
        print("* No response from the rpc.")
    print(Fore.MAGENTA)
    print_stars()
    print("* Press enter to return to the main menu.")
    print_stars()
    input()

def refresh_fn_stats() -> None:
    subprocess.run("clear")
    print_stars()
    try:
        output = subprocess.check_output(["fn", "show"])
        output = output.decode().replace("b'", "")
        print(output)
    except:
        print(
            "* Error, no response from local API, try your curl stats again. If the stats give the same reply try option #10 to get back online and as a last resort option #12!"
        )
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
    print(Fore.MAGENTA)
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
    subprocess.call(["bash", "-x", f"/tmp/update_{environ.get('FRA_NETWORK')}.sh"], cwd=easy_env_fra.user_home_dir)

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
        subprocess.call(
            ["bash", "-x", f"/tmp/fn_update_{environ.get('FRA_NETWORK')}.sh"], cwd=easy_env_fra.user_home_dir
        )
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
    question = ask_yes_no(f"* You will miss blocks while upgrades run.\n* Are you sure you want to run updates? (Y/N) ")
    if question:
        subprocess.run("clear")
        print_stars()
        print(f"* Stopping docker container for safety")
        subprocess.call(["docker", "container", "stop", "findorad"])
        run_ubuntu_updater()
        print_stars()
        print(f"* Restarting findorad container")
        subprocess.call(["docker", "container", "start", "findorad"])
        refresh_fn_stats()
    else:
        return

def chown_dir(root_dir, user, group) -> None:
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            os.chown(os.path.join(root, file), user, group)
        for dir in dirs:
            os.chown(os.path.join(root, dir), user, group)

def get_uid() -> None:
    user_name = getpass.getuser()
    user_info = pwd.getpwnam(user_name)
    uid = user_info.pw_uid
    return uid

def migrate_to_server() -> None:
    if os.path.exists(f"{easy_env_fra.migrate_dir}"):
        # check for tmp.gen.keypair and priv_validator_key.json in ~/migrate
        print(f"* You have a migrate folder, checking for files.")
        if os.path.exists(f"{easy_env_fra.migrate_dir}/tmp.gen.keypair") and os.path.exists(
            f"{easy_env_fra.migrate_dir}/config/priv_validator_key.json"
        ) or os.path.exists(f"{easy_env_fra.migrate_dir}/priv_validator_key.json"):
            print(
                f"* {easy_env_fra.migrate_dir}/tmp.gen.keypair found!\n* {easy_env_fra.migrate_dir}/config/priv_validator_key.json found!\n* All required files in place, ready for upgrade!"
            )
            # Ask to start migration, warn about double sign again, again
            print_stars()
            answer = ask_yes_no(
                f"* Are you sure your old server is shut down? Files to migrate have been detected.\n* One last time, are you sure you want to migrate and start-up now? (Y/N) "
            )
            if answer:
                print_stars()
                # start installing
                print('* Copying Files...')
                # stop service
                subprocess.call(["docker", "container", "stop", "findorad"])
                # move files
                if os.path.exists(f'{easy_env_fra.findora_root}/{environ.get("FRA_NETWORK")}/{environ.get("FRA_NETWORK")}_node.key'): os.remove(f'{easy_env_fra.findora_root}/{environ.get("FRA_NETWORK")}/{environ.get("FRA_NETWORK")}_node.key')
                shutil.copy(f'{easy_env_fra.migrate_dir}/tmp.gen.keypair', f'{easy_env_fra.findora_root}/{environ.get("FRA_NETWORK")}/{environ.get("FRA_NETWORK")}_node.key')
                os.remove(f'{easy_env_fra.findora_root}/{environ.get("FRA_NETWORK")}/tendermint/config/priv_validator_key.json')
                if os.path.exists(f'{easy_env_fra.migrate_dir}/priv_validator_key.json'): 
                    shutil.copy(f'{easy_env_fra.migrate_dir}/priv_validator_key.json', f'{easy_env_fra.findora_root}/{environ.get("FRA_NETWORK")}/tendermint/config/priv_validator_key.json')
                elif os.path.exists(f'{easy_env_fra.migrate_dir}/config/priv_validator_key.json'):
                    shutil.copy(f'{easy_env_fra.migrate_dir}/config/priv_validator_key.json', f'{easy_env_fra.findora_root}/{environ.get("FRA_NETWORK")}/tendermint/config/priv_validator_key.json')
                else:
                    print("* Welp, somehow we didn't find a priv_validator_key.json to migrate.\n* You'll have to get your key into the config folder and run a safety clean.")
                node_mnemonic = subprocess.getoutput(f"cat {easy_env_fra.migrate_dir}/tmp.gen.keypair | grep 'Mnemonic' | sed 's/^.*Mnemonic:[^ ]* //'")
                os.remove(f"{easy_env_fra.findora_root}/{environ.get('FRA_NETWORK')}/node.mnemonic")
                subprocess.call(["touch", f"{easy_env_fra.findora_root}/{environ.get('FRA_NETWORK')}/node.mnemonic"])
                with open(f"{easy_env_fra.findora_root}/{environ.get('FRA_NETWORK')}/node.mnemonic", "w") as file:
                    file.write(node_mnemonic)
                print(f'* File copying completed, restarting services.')
                # Restart container
                migration_update()
                print_stars()
                print(f'* Migration completed, check option #2 to verify your validator information has updated correctly!')

        else:
            print(
                f"* We're sorry, your folder is there but you are missing file(s), please try again after fixing the contents.\n* Add the files from your old server into:\n* {easy_env_fra.migrate_dir}/tmp.gen.keypair\n* {easy_env_fra.migrate_dir}/config/priv_validator_key.json\n*"
            )
    else:
        # path doesn't exist, explain migration process.
        print(
            f"* We didn't locate a folder at {easy_env_fra.migrate_dir}\n*\n* Exit the toolbox, then:\n* 1. Make a folder named {easy_env_fra.migrate_dir}\n* 2. Add your tmp.gen.keypair file into the folder\n* 3. Add your config folder containing your priv_validator_key.json file into migrate\n* 4. If this server is synced up, you can shut off your old server and run migration again at that point to move servers without double signing.\n*\n* The goal is to avoid double signing and a 5% slashing fee!!!\n*\n* Load your files and run this option again!"
        )
    print_stars()
    print("* Press enter to return to the main menu.")
    print_stars()
    input()
    return

def run_container_update(status=False) -> None:
    update_findora_container(status)

def migration_menu_option() -> None:
    if os.path.exists(f'{easy_env_fra.migrate_dir}/tmp.gen.keypair') and os.path.exists(f'{easy_env_fra.migrate_dir}/priv_validator_key.json') or os.path.exists(f"{easy_env_fra.migrate_dir}/priv_validator_key.json"):
        print(f'* 888 -  {Fore.CYAN}Migrate To This Server    {Fore.MAGENTA}- Migrate from another server to this server.')

def run_findora_menu() -> None:
    menu_options = {
        0: finish_node,
        1: refresh_wallet_stats,
        2: refresh_fn_stats,
        3: check_balance_menu,
        4: coming_soon,
        5: coming_soon,
        6: coming_soon,
        7: update_fn_wallet,
        8: run_container_update,
        9: run_clean_script,
        10: run_ubuntu_updates,
        11: coming_soon,
        12: coming_soon,
        13: server_disk_check,
        14: coming_soon,
        15: all_sys_info,
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
        menu_options[value]()
