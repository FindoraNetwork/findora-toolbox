import os
import subprocess
from subprocess import run
from toolbox.library import loader_intro, print_stars, docker_check
from library import run_findora_menu, findora_installer, update_findora_container
from colorama import Fore
from config import easy_env_fra
# Check the status and print a message

def main() -> None:
    # Wear purple
    print(Fore.MAGENTA)
    # Intro w/ stars below
    loader_intro()
    print_stars()
    # Can we use docker on this user?
    docker_check()
    # Does `fn` exist?
    if os.path.exists('/usr/local/bin/fn') is False:
        # Nope, let's ask to install!
        findora_installer()
    # fn is found, is the container running? Run the 'docker ps' command and filter the output using 'grep'
    status = subprocess.call(["docker", "ps", "--filter", f"name={easy_env_fra.container_name}"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # Check the status and print a message
    if status == 0:
        # Launch menu, we're good to go!
        print(f"* The container '{easy_env_fra.container_name}' is running. Press enter to continue.")
        print_stars()
        input()
        
        run_findora_menu()

    else:
        # Container is not running, ruh roh!
        print(f"* The container '{container_name}' is not running.")
        print(f"* We will attempt to get the findorad container online now, press ctrl+c to cancel or enter to continue.")
        print_stars()
        input()
        update_findora_container()
    print_stars()

if __name__ == "__main__":
    while True:
        main()
    