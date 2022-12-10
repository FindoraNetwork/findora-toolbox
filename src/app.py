import os
import subprocess
from subprocess import run
from toolbox.library import loader_intro, print_stars, ask_yes_no
from toolbox.toolbox import menu_error
from library import docker_check, menu_findora, run_findora_menu

# Check the status and print a message

if __name__ == "__main__":
    loader_intro()
    print_stars()
    docker_check()
    if os.path.exists('/usr/local/bin/fn') is False:
        # Run installer ya'll!
        print(f'* Welcome to EasyNode.PRO Validator Toolbox for Findora!')
        print(f"* We've detected that Docker is properly installed for this user, excellent!")
        print(f"* It doesn't look like you have Findora installed.")
        print(f"* We will setup Findora validator on this server with a brand new wallet and start syncing with the blockchain.")
        answer = ask_yes_no(f'* Do you want to install it now? (Y/N) ')
        if answer:
            subprocess.run('wget https://raw.githubusercontent.com/easy-node-pro/findora-validator-scripts/main/easy_install_mainnet.sh -O install_mainnet.sh && bash -x install_mainnet.sh')
            print_stars()
            print(f'* Setup has completed. Once you are synced up (catching_up=False) you are ready to create your validator on-chain or migrate from another server onto this server.')
            raise SystemExit(0)
        print_stars()
    else:
        # fn is found, is the container running?
        # Set the container name
        container_name = "findorad"

        # Run the 'docker ps' command and filter the output using 'grep'
        status = subprocess.call(["docker", "ps", "--filter", f"name={container_name}"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        # Check the status and print a message
        if status == 0:
            # Launch menu, we're good to go!
            print(f"* The container '{container_name}' is running.")
            print_stars()
            run_findora_menu()

        else:
            # Container is not running, ruh roh!
            print(f"* The container '{container_name}' is not running.")
        print_stars()
