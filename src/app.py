import os
import argparse
from toolbox import (
    run_fractal_menu,
    menu_install_fractal,
    backup_folder_check,
    print_stars,
    loader_intro,
    check_container_running,
    run_troubleshooting_process,
    parse_flags,
    check_preflight_setup,
    old_version_check,
)
from config import config


def main() -> None:
    print_stars()
    print("* Welcome to the Fractal Validator Toolbox!")
    print_stars()

    # Check for previous version of the toolbox and convert old config files
    old_version_check()

    # Check & Load Vars / Set Network & Region
    network, region = check_preflight_setup(
        config.dotenv_file, config.user_home_dir, config.active_user_name
    )
    
    print("test after check preflight setup")

    # If `fn` isn't installed, run full installer.
    if not os.path.exists("/usr/local/bin/fn"):
        # It does not, let's ask to install!
        menu_install_fractal(network, region)

    # Init parser for extra flags:
    parser = argparse.ArgumentParser(
        description="Fractal Validator Toolbox - Help Menu"
    )
    parse_flags(parser, region, network)

    # Can this user access docker and is our container up?
    if check_container_running(config.container_name):

        # Print Loading
        print("* Gathering Validator Information... ")
        print_stars()

        # Intro
        loader_intro()
        print_stars()
        print("* Loading Validator Menu...")

        # fn is found, is the fractal container running? Run the 'docker ps' command and filter the output using 'grep'

        backup_folder_check()
        run_fractal_menu()
    else:
        # fn found, container not online, run troubleshooting process
        run_troubleshooting_process()


if __name__ == "__main__":
    while True:
        main()
