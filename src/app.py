import os
import subprocess
from os import environ
from subprocess import run
from toolbox.library import loader_intro, print_stars, docker_check, container_running, finish_node, menu_error, set_main_or_test, load_var_file, first_env_check
from library import run_findora_menu, findora_installer, update_findora_container, refresh_wallet_stats, run_clean_script
from colorama import Fore
from config import easy_env_fra
# Check the status and print a message

def main(count) -> None:
    # Wear purple
    print(Fore.MAGENTA)
    # Load Vars
    first_env_check(easy_env_fra.dotenv_file, easy_env_fra.user_home_dir)
    # Intro w/ stars below
    loader_intro()
    print_stars()
    # Can we use docker on this user?
    docker_check()
    # Does `fn` exist?
    if not os.path.exists('/usr/local/bin/fn'):
        # Nope, let's ask to install!
        findora_installer()
    # fn is found, is the container running? Run the 'docker ps' command and filter the output using 'grep'
    # do we know network?
    if environ.get("NETWORK") is False:
        set_main_or_test()
    if container_running(easy_env_fra.container_name):
        # Launch menu, we're good to go!
        print(f"* The container '{easy_env_fra.container_name}' is running.")
        print_stars()
        
        run_findora_menu()

    else:
        # Container is not running, ruh roh!
        if count == 0:
            print(f"* The container '{easy_env_fra.container_name}' is not running.")
            print(f"* We will attempt to get the findorad container online now, press ctrl+c to cancel or enter to continue.")
            print_stars()
            input()
            update_findora_container(1)
        else:
            menu_options = {
                0: finish_node,
                1: refresh_wallet_stats,
                2: run_clean_script
            }
            print(f"* We still don't detect a running container. Here are your options currently:\n* 1 - Keep checking stats, wait longer and retry.\n* 2 - Run safety clean and reset data.\n* 0 - Exit and manually troubleshoot")
            print_stars()
            try:
                option = int(input("Enter your option: "))
            except ValueError:
                menu_error()
                main(1)
            os.system("clear")
            menu_options[option]()
            main(1)
    print_stars()

if __name__ == "__main__":
    count = 0
    while True:
        main(count)
        count += 1
    