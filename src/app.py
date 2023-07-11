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
    set_na_or_eu
)
from colorama import Fore
from config import findora_env

# Check the status and print a message


def main() -> None:
    # Preflight check:
    if os.path.exists(f'{findora_env.user_home_dir}/validatortoolbox_fra'):
        subprocess.run('clear') 
        print(Fore.MAGENTA)
        print_stars()
        print('*\n* Old folder found, Exiting\n*\n* Please rename your ~/validatortoolbox_fra'
              + 'folder to ~/findora-toolbox and update your command paths!\n*\n* To rename, run:'
              + ' cd ~/ && mv ~/validatortoolbox_fra ~/findora-toolbox\n*\n* After you run the'
              + ' move command, relaunch with the new path: python3 ~/findora-toolbox/src/app.py\n*')
        print_stars()
        raise SystemExit(0)
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
    parser = argparse.ArgumentParser(description='Findora Validator Toolbox - Help Menu')
    parse_flags(parser)
    # Does `fn` exist?
    if not os.path.exists("/usr/local/bin/fn"):
        # Nope, let's ask to install!
        menu_install_findora(network, region)
    # fn is found, is the container running? Run the 'docker ps' command and filter the output using 'grep'
    if container_running(findora_env.container_name):
        backup_folder_check()
        run_findora_menu()
    else:
        print(f"* The container '{findora_env.container_name}' is not running.")
        while True:
            answer = ask_yes_no(
                "* Would you like to attempt to run the update version script to try to get your container back online? (Y/N)"
            )
            if answer:
                update_findora_container(1)
                print("* Uh, you said no so, we are exiting to allow manual troubleshooting, goodbye!")
                finish_node()
            else:
                answer2 = ask_yes_no("* Would you like to load the rescue menu to try and troubleshoot? (Y/N) ")
                if answer2:
                    rescue_menu()
                else:
                    print(
                        "* Dropping out of the application so you can troubleshoot the container, check the docker logs with: docker logs -f findorad"
                    )
                    print_stars()
                    finish_node()


if __name__ == "__main__":

    while True:
        main()
