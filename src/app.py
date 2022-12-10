import os
import subprocess
from subprocess import run
from toolbox.library import loader_intro, print_stars, ask_yes_no
from toolbox.toolbox import menu_error
from library import docker_check, menu_findora, run_findora_menu, findora_installer
from colorama import Fore
# Check the status and print a message

if __name__ == "__main__":
    print(Fore.MAGENTA)
    loader_intro()
    print_stars()
    docker_check()
    if os.path.exists('/usr/local/bin/fn') is False:
        findora_installer()
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
