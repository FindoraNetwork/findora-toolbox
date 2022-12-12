import os
import subprocess
from os import environ
from subprocess import run
from toolbox.library import loader_intro, print_stars, docker_check, container_running, finish_node, menu_error, load_var_file, first_env_check, ask_yes_no
from library import run_findora_menu, findora_installer, update_findora_container, refresh_wallet_stats, run_clean_script, set_main_or_test, rescue_menu
from colorama import Fore
from config import easy_env_fra
# Check the status and print a message

def main(count) -> None:
    # Wear purple
    print(Fore.MAGENTA)
    # Intro w/ stars below
    loader_intro()
    print_stars()
    # Load Vars / Set Network
    first_env_check(easy_env_fra.dotenv_file, easy_env_fra.user_home_dir)
    # Can we use docker on this user?
    docker_check()
    # Does `fn` exist?
    if not os.path.exists('/usr/local/bin/fn'):
        # Nope, let's ask to install!
        findora_installer()
    # fn is found, is the container running? Run the 'docker ps' command and filter the output using 'grep'
    # do we know network?
    if not environ.get("FRA_NETWORK"):
        set_main_or_test()
    if container_running(easy_env_fra.container_name):
        run_findora_menu()
    # Container is not running, ruh roh!
    print(f"* The container '{easy_env_fra.container_name}' is not running.")
    count = 0
    while True:
        answer = ask_yes_no(f"* Would you like to attempt to run the update version script to try to get your container back online? (Y/N)")
        if answer:
            update_findora_container(1)
            print(f'* Uh, you said no so, we are exiting to allow manual troubleshooting, goodbye!')
            raise SystemExit(0)              
        else:
            answer2 = ask_yes_no(f"* Would you like to load the rescue menu to try and troubleshoot? (Y/N) ")
            if answer2:
                rescue_menu()
            else:
                print(f"* Dropping out of the application so you can troubleshoot the container, check the docker logs with: docker logs -f findorad")
                print_stars()
                raise SystemExit(0)
        

if container_running(easy_env_fra.container_name):
    print_stars()
    print(f'* Your container is restarted and back online. Press enter to return to the main menu.')
    input()
    run_findora_menu()
else:
    print_stars()
    print(f'* Your container was restarted but there was a problem bringing it back online.\n*\n* Starting the rescue menu now. Press enter to load the menu or ctrl+c to quit and manually troubleshoot.')
    input()
    rescue_menu()

if __name__ == "__main__":
    count = 0
    while True:
        main(count)
        count += 1
    