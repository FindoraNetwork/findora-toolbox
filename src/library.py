import subprocess
import os
import time
import json
import shutil
import pwd
import getpass
import requests
from simple_term_menu import TerminalMenu
from os import environ
from colorama import Fore, Back, Style
from pprint import pprint
from toolbox.library import (
    print_stars,
    print_stars_reset,
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
    compare_two_files,
    container_running,
)
from config import easy_env_fra


def pause_for_cause():
    print(Fore.MAGENTA)
    print_stars()
    print("* Press enter to return to the main menu.")
    print_stars()
    input()


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
    update = menu_topper()
    print("* EasyNode.PRO Findora Validator Toolbox Menu Options:")
    print("*")
    print("*   1 -  Show 'curl' stats info    - Run this to show your local curl stats!")
    print("*   2 -  Show 'fn' stats info      - Run this to show your local fn stats!")
    print("*   3 -  Show Balance              - Check Any Wallet Balance")
    print("*   7 -  Update fn Application     - Pull update for the wallet application, fn")
    print(f"*                                   {Fore.CYAN}{Back.RED}The Danger Zone:{Style.RESET_ALL}{Fore.MAGENTA}")
    findora_container_update(update)
    print("*   9 -  Run Safety Clean          - Stop your container, reset and download database fresh")
    print("*  10 -  Update Operating System   - Update Ubuntu Operating System Files")
    print(
        f"*                                   {Fore.MAGENTA}{Back.GREEN}Informational Section:{Style.RESET_ALL}{Fore.MAGENTA}"
    )
    print("*  13 -  Show system disk info     - Current drive space status")
    print("*  14 -  TMI about your Validator  - Seriously too much information")
    print("*  15 -  TMI about your Server     - Seriously a lot of info about this server")
    print("*  16 -  Instructions on Migrating - Run this to read info on migrating to this server.")
    print_stars()
    migration_menu_option()
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
    subprocess.run("clear")
    print_stars()
    print(Fore.GREEN)
    try:
        output = subprocess.check_output(["curl", "http://localhost:26657/status"])
        output = output.decode().replace("b'", "")
        output = json.loads(output)
        pprint(output)
    except subprocess.CalledProcessError as err:
        print(f"* No response from the rpc. Error: {err}")
    print(Fore.MAGENTA)
    pause_for_cause()
    return


def refresh_fn_stats() -> None:
    subprocess.run("clear")
    print_stars()
    try:
        output = subprocess.check_output(["fn", "show"])
        output = output.decode().replace("b'", "")
        print(output)
    except subprocess.CalledProcessError as err:
        print(
            "* Error, no response from local API, try your curl stats again. If the stats give the "
            + "same reply try option #10 to get back online and as a last resort option #12!\n"
            + f"* Error: {err}"
        )
    pause_for_cause()


def check_balance_menu() -> None:
    print("* Coming soon!")
    print_stars()
    input("* Press ENTER to continue.")


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
    print_stars()
    input("* Disk check complete, press ENTER to return to the main menu. ")


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
        print("*   8 -  Update Findora Container  - Pull & Restart the latest container from Findora")
        return


def menu_topper() -> None:
    Load1, Load5, Load15 = os.getloadavg()
    # get sign pct
    # get balances
    # get other validator data
    try:
        our_version = get_container_version("http://localhost:8668/version")
    except TimeoutError:
        our_version = "No Response"
        print_stars()
        print(
            "* Container is running but there is no response from http://localhost:8668/version - Are your ports open?"
            + "\n* We can continue though, press enter to load the menu."
        )
        print_stars()
    try:
        online_version = get_container_version(
            f'https://{easy_env_fra.fra_env}-{environ.get("FRA_NETWORK")}.{easy_env_fra.fra_env}.findora.org:8668/version'
        )
    except TimeoutError:
        online_version = "No Response"
        print_stars()
        print(
            "* No response from findora node, network may be offline or there are internet troubles"
            + "\n* We can continue though, press enter to load the menu."
        )
        print_stars()
        input()
    subprocess.run("clear")
    print(Fore.MAGENTA)
    print_stars()
    print(
        f"{Style.RESET_ALL}{Fore.MAGENTA}* {Fore.MAGENTA}validator-toolbox for Findora FRA Validators by Easy Node"
        + f"   v{easy_env_fra.easy_version}{Style.RESET_ALL}{Fore.MAGENTA}   https://easynode.pro *"
    )
    print_stars()
    print(
        f"* Server Hostname & IP:             {easy_env_fra.server_host_name}{Style.RESET_ALL}{Fore.MAGENTA}"
        + f" - {Fore.YELLOW}{easy_env_fra.our_external_ip}{Style.RESET_ALL}{Fore.MAGENTA}"
    )
    print(
        f"* Current disk space free: {Fore.CYAN}{free_space_check(easy_env_fra.findora_root): >6}{Style.RESET_ALL}{Fore.MAGENTA}"
    )
    print(f"* Current Container Version: {our_version}")
    if online_version != our_version:
        print(f"* Container Update Available: {online_version}")
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
    menu_options = {0: finish_node, 1: get_curl_stats, 2: run_container_update, 3: run_clean_script}
    print(
        "* We still don't detect a running container. Here are your options currently:"
        + "\n* 1 - Keep checking stats, wait longer and retry."
        + "\n* 2 - Run update version and restart script."
        + "\n* 3 - Run safety clean and reset data."
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
    print("* Running the update and restart may cause missed blocks, beware before proceeding!")
    if skip:
        answer = True
    else:
        answer = ask_yes_no("* Are you sure you want to check for an upgrade and restart? (Y/N) ")
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
        subprocess.call(["bash", "-x", f"/tmp/update_{environ.get('FRA_NETWORK')}.sh"], cwd=easy_env_fra.user_home_dir)
        if container_running(easy_env_fra.container_name):
            print_stars()
            print("* Your container is restarted and back online. Press enter to return to the main menu.")
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
            ["bash", "-x", f"/tmp/fn_update_{environ.get('FRA_NETWORK')}.sh"], cwd=easy_env_fra.user_home_dir
        )
        print_stars()
        input("* Fn update complete, press ENTER to return to the main menu. ")
        return


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
            ["bash", "-x", f"/tmp/safety_clean_{environ.get('FRA_NETWORK')}.sh"], cwd=easy_env_fra.user_home_dir
        )
        if container_running(easy_env_fra.container_name):
            print_stars()
            print("* Your container is restarted and back online. Press enter to return to the main menu.")
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


def findora_installer() -> None:
    # Run installer ya'll!
    print(
        "* Welcome to EasyNode.PRO Validator Toolbox for Findora!\n* We've detected that Docker is properly installed for this user, excellent!"
        + "\n* It doesn't look like you have Findora installed."
        + "\n* We will setup Findora validator on this server with a brand new wallet and start syncing with the blockchain."
    )
    answer = ask_yes_no("* Do you want to install it now? (Y/N) ")
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
            "* We will show the output of the installation, this will take some time to download and unpack.\n* Starting Findora installation now."
        )
        print_stars()
        time.sleep(3)
        print_stars()
        subprocess.call(["bash", "-x", f"/tmp/install_{environ.get('FRA_NETWORK')}.sh"], cwd=easy_env_fra.user_home_dir)
        print_stars()
        print(
            "* Setup has completed. Once you are synced up (catching_up=False) you are ready to create your "
            + "validator on-chain or migrate from another server onto this server.\n* Press enter to continue."
        )
        print_stars()
        input()
    else:
        raise SystemExit(0)


def run_ubuntu_updates() -> None:
    question = ask_yes_no("* You will miss blocks while upgrades run.\n* Are you sure you want to run updates? (Y/N) ")
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
    pause_for_cause()


def migrate_to_server() -> None:
    if os.path.exists(f"{easy_env_fra.migrate_dir}"):
        # check for tmp.gen.keypair and priv_validator_key.json in ~/migrate
        print("* You have a migrate folder, checking for files.")
        if (
            os.path.exists(f"{easy_env_fra.migrate_dir}/tmp.gen.keypair")
            and os.path.exists(f"{easy_env_fra.migrate_dir}/config/priv_validator_key.json")
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
                shutil.copy(
                    f"{easy_env_fra.migrate_dir}/tmp.gen.keypair",
                    f'{easy_env_fra.findora_root}/{environ.get("FRA_NETWORK")}/{environ.get("FRA_NETWORK")}_node.key',
                )
                os.remove(
                    f'{easy_env_fra.findora_root}/{environ.get("FRA_NETWORK")}/tendermint/config/priv_validator_key.json'
                )
                if os.path.exists(f"{easy_env_fra.migrate_dir}/priv_validator_key.json"):
                    shutil.copy(
                        f"{easy_env_fra.migrate_dir}/priv_validator_key.json",
                        f'{easy_env_fra.findora_root}/{environ.get("FRA_NETWORK")}/tendermint/config/priv_validator_key.json',
                    )
                elif os.path.exists(f"{easy_env_fra.migrate_dir}/config/priv_validator_key.json"):
                    shutil.copy(
                        f"{easy_env_fra.migrate_dir}/config/priv_validator_key.json",
                        f'{easy_env_fra.findora_root}/{environ.get("FRA_NETWORK")}/tendermint/config/priv_validator_key.json',
                    )
                else:
                    print(
                        "* Welp, somehow we didn't find a priv_validator_key.json to migrate."
                        + "\n* You'll have to get your key into the config folder and run a safety clean."
                    )
                node_mnemonic = subprocess.getoutput(
                    f"cat {easy_env_fra.migrate_dir}/tmp.gen.keypair | grep 'Mnemonic' | sed 's/^.*Mnemonic:[^ ]* //'"
                )
                os.remove(f"{easy_env_fra.findora_root}/{environ.get('FRA_NETWORK')}/node.mnemonic")
                subprocess.call(["touch", f"{easy_env_fra.findora_root}/{environ.get('FRA_NETWORK')}/node.mnemonic"])
                with open(f"{easy_env_fra.findora_root}/{environ.get('FRA_NETWORK')}/node.mnemonic", "w") as file:
                    file.write(node_mnemonic)
                print("* File copying completed, restarting services.")
                # Wipe backup folder and re-create
                timestamp = time.strftime("%Y%m%d-%H%M%S")
                backup_dir = f"{easy_env_fra.user_home_dir}/findora_backup_{format(timestamp)}"
                shutil.copytree(easy_env_fra.findora_backup, backup_dir)
                shutil.rmtree(f"{easy_env_fra.findora_backup}")
                backup_folder_check()
                # Restart container
                migration_update()
                shutil.rmtree(easy_env_fra.migrate_dir)
                print_stars()
                print(
                    "* Migration completed, check option #2 to verify your validator information has updated correctly!"
                )
                pause_for_cause()

        else:
            print(
                "* We're sorry, your folder is there but you are missing file(s), please try again after fixing the contents."
                + f"\n* Add the files from your old server into:\n* {easy_env_fra.migrate_dir}/tmp.gen.keypair"
                + f"\n* {easy_env_fra.migrate_dir}/config/priv_validator_key.json\n*"
            )
            pause_for_cause()
    else:
        migration_instructions()
    return


def run_container_update(status=False) -> None:
    update_findora_container(status)
    return


def migration_menu_option() -> None:
    file_paths = {}
    if os.path.exists(f"{easy_env_fra.migrate_dir}/tmp.gen.keypair"):
        file_paths["tmp.gen.keypair"] = f"{easy_env_fra.migrate_dir}/tmp.gen.keypair"
    else:
        # No tmp.gen.keypair, we're out.
        return
    if os.path.exists(f"{easy_env_fra.migrate_dir}/priv_validator_key.json"):
        file_paths["priv_validator_key.json"] = f"{easy_env_fra.migrate_dir}/priv_validator_key.json"
    elif os.path.exists(f"{easy_env_fra.migrate_dir}/config/priv_validator_key.json"):
        file_paths["priv_validator_key.json"] = f"{easy_env_fra.migrate_dir}/config/priv_validator_key.json"
    else:
        # No matches on priv_validator_key.json, we're out.
        return
    if compare_two_files(
        file_paths["tmp.gen.keypair"],
        f'{easy_env_fra.findora_root}/{environ.get("FRA_NETWORK")}/{environ.get("FRA_NETWORK")}_node.key',
    ):
        # If these are the same, already migrated, don't display
        return
    if compare_two_files(
        file_paths["priv_validator_key.json"],
        f'{easy_env_fra.findora_root}/{environ.get("FRA_NETWORK")}/tendermint/config/priv_validator_key.json',
    ):
        # If these are the same, already migrated, don't display
        return
    print(f"* 888 -  {Fore.CYAN}Migrate To This Server    {Fore.MAGENTA}- Migrate from another server to this server.")


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
        16: migration_instructions,
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
