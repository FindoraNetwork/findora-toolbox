import os, argparse, subprocess
from os import environ
from library import (
    run_findora_menu,
    menu_install_findora,
    update_findora_container,
    set_main_or_test,
    rescue_menu,
    backup_folder_check,
    print_stars,
    loader_intro,
    docker_check,
    container_running,
    finish_node,
    ask_yes_no,
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
        print(f"* Docker is running and working but the container '{findora_env.container_name}' is not.")
        while True:
            answer = ask_yes_no(
                "* Would you like to attempt to run the update_version script to try to get your container back online? (Y/N)"
            )
            if answer:
                update_findora_container(True)
                break
            else:
                answer2 = ask_yes_no("* Would you like to load the rescue menu to try and troubleshoot (Select N to exit and manually troubleshoot)? (Y/N) ")
                if answer2:
                    rescue_menu()
                else:
                    print(
                        "* Stopping toolbox so you can troubleshoot the container manually.\n"
                        + "* Here's what we suggest in order to try to troubleshoot:\n\n* 1 - Check docker logs for errors with: docker logs findorad\n"
                        + "* 2 - Restart the toolbox with the -u flag to run the upgrade_script: ./findora.sh -u\n"
                        + "* If the above does not work you should be prompted to run a safety clean or you can do that manually with: ./findora.sh --clean\n"
                        + "* If you are still having issues please reach out on our Discord: https://bit.ly/easynodediscord\n"
                    )
                    print_stars()
                    finish_node()


if __name__ == "__main__":
    while True:
        main()
