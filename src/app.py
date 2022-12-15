import os
from os import environ
from toolbox.library import loader_intro, print_stars, docker_check, container_running, finish_node, first_env_check, ask_yes_no
from library import run_findora_menu, findora_installer, update_findora_container, set_main_or_test, rescue_menu, backup_folder_check
from colorama import Fore
from config import easy_env_fra
# Check the status and print a message

def main() -> None:
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
        backup_folder_check()
        run_findora_menu()
    # Container is not running, ruh roh!
    print(f"* The container '{easy_env_fra.container_name}' is not running.")
    while True:
        answer = ask_yes_no("* Would you like to attempt to run the update version script to try to get your container back online? (Y/N)")
        if answer:
            update_findora_container(1)
            print('* Uh, you said no so, we are exiting to allow manual troubleshooting, goodbye!')
            finish_node()
        else:
            answer2 = ask_yes_no("* Would you like to load the rescue menu to try and troubleshoot? (Y/N) ")
            if answer2:
                rescue_menu()
            else:
                print("* Dropping out of the application so you can troubleshoot the container, check the docker logs with: docker logs -f findorad")
                print_stars()
                finish_node()

if __name__ == "__main__":
    while True:
        main()

    