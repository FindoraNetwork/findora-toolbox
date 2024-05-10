import os
import argparse
from toolbox import (
    run_findora_menu,
    menu_install_findora,
    backup_folder_check,
    print_stars,
    loader_intro,
    docker_check,
    container_running,
    run_troubleshooting_process,
    parse_flags,
    check_preflight_setup,
    finish_node,
)
from config import config


def main() -> None:
    # Intro w/ stars below
    loader_intro()
    print_stars()
    
    if os.path.exists("~/.findora.env"):
        print_stars()
        print("You have a previous version of the Findora Toolbox installed. Please remove it before continuing.")
        print("Run the following command to remove the previous version:")
        print("wget https://raw.githubusercontent.com/FindoraNetwork/findora-toolbox/main/src/bin/fractal.sh && chmod +x fractal.sh && rm ~/findora.sh && mv ~/findora-toolbox ~/fractal-toolbox && mv .findora.env .fractal.env && ./fractal.sh -u")
        print_stars()
        finish_node()

    # Load Vars / Set Network & Region
    network, region = check_preflight_setup(
        config.dotenv_file, config.user_home_dir, config.active_user_name
    )

    # Can this user access docker?
    docker_check()
    
    # Print Loading
    print('* Gathering API Information... ')
    print_stars()

    # Init parser for extra flags:
    parser = argparse.ArgumentParser(description="Findora Validator Toolbox - Help Menu")
    parse_flags(parser, region, network)

    # If `fn` isn't installed, run full installer.
    if not os.path.exists("/usr/local/bin/fn"):
        # It does not, let's ask to install!
        menu_install_findora(network, region)
    # fn is found, is the fractal container running? Run the 'docker ps' command and filter the output using 'grep'
    elif container_running(config.container_name):
        backup_folder_check()
        run_findora_menu()
    else:
        # fn found, container not online, run troubleshooting process
        run_troubleshooting_process()


if __name__ == "__main__":
    while True:
        main()
