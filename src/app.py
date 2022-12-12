import os
import subprocess
from os import environ
from subprocess import run
from toolbox.library import loader_intro, print_stars, docker_check, container_running, finish_node, menu_error, load_var_file, first_env_check, ask_yes_no
from library import run_findora_menu, findora_installer, update_findora_container, refresh_wallet_stats, run_clean_script, set_main_or_test
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
    else:
        # Container is not running, ruh roh!
        if count == 0:
            print(f"* The container '{easy_env_fra.container_name}' is not running.")
            answer = ask_yes_no(f"* Would you like to attempt to run the update version script to try to get your container back online? (Y/N)")
            if answer:
                update_findora_container(1)
                run_findora_menu()
            else:
                answer2 = ask_yes_no(f"* Would you like to load the toolbox menu? (Y/N) ")
                if answer2:
                    run_findora_menu()
                else:
                    print(f"* Dropping out of the application so you can troubleshoot the container, check the docker logs with: docker logs -f findorad")
                    print_stars()
                    raise SystemExit(0)
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
            subprocess.run("clear")
            menu_options[option]()
            main(1)
    print_stars()

if __name__ == "__main__":
    count = 0
    while True:
        main(count)
        count += 1
    