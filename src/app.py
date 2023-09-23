import os, argparse, subprocess
from os import environ
from library import (
    run_findora_menu,
    menu_install_findora,
    set_main_or_test,
    backup_folder_check,
    print_stars,
    loader_intro,
    docker_check,
    container_running,
    run_troubleshooting_process,
    parse_flags,
    set_na_or_eu,
    first_env_check,
)
from colorama import Fore
from config import findora_env

# Check the status and print a message


def main() -> None:
    # Load Vars / Set Network
    first_env_check(findora_env.dotenv_file, findora_env.user_home_dir)
    # Wear purple
    print(Fore.MAGENTA)
    # Intro w/ stars below
    loader_intro()
    print_stars()
    # Can we use docker on this user?
    docker_check()
    # do we know network? mainnet or testnet
    network = set_main_or_test()
    region = set_na_or_eu()
    # Init parser for flags:
    parser = argparse.ArgumentParser(description="Findora Validator Toolbox - Help Menu")
    parse_flags(parser, region, network)
    # Does `fn` exist?
    if not os.path.exists("/usr/local/bin/fn"):
        # It does not, let's ask to install!
        menu_install_findora(network, region)
    # fn is found, is the findorad container running? Run the 'docker ps' command and filter the output using 'grep'
    if container_running(findora_env.container_name):
        backup_folder_check()
        run_findora_menu()
    else:
        run_troubleshooting_process()


if __name__ == "__main__":
    while True:
        main()
