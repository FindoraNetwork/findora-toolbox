import os
import argparse
from toolbox import (
    run_findora_menu,
    menu_install_fractal,
    backup_folder_check,
    print_stars,
    loader_intro,
    check_container_running,
    run_troubleshooting_process,
    parse_flags,
    check_preflight_setup,
    finish_node,
)
from config import config


def main() -> None:
    print_stars()
    print("* Welcome to the Fractal Validator Toolbox!")
    print_stars()

    # Check for previous version of the toolbox, halt if found until upgraded manually
    if os.path.exists(f"{config.user_home_dir}/.findora.env"):
        print(
            "* WARNING: You have the Findora Toolbox installed and not the new Fractal Toolbox."
        )
        print_stars()
        print(
            "* Please run the following command to convert from the findora toolbox to fractal toolbox and start the upgrade process:"
        )
        print()
        print(
            "cd && wget -O fractal.sh https://raw.githubusercontent.com/FindoraNetwork/findora-toolbox/main/src/bin/fractal.sh\n"
        )
        print(
            "&& chmod +x fractal.sh && rm ~/findora.sh && mv ~/findora-toolbox ~/fractal-toolbox && mv .findora.env .fractal.env && ./fractal.sh -u"
        )
        print()
        print_stars()
        finish_node()

    # Check & Load Vars / Set Network & Region
    network, region = check_preflight_setup(
        config.dotenv_file, config.user_home_dir, config.active_user_name
    )

    # If `fn` isn't installed, run full installer.
    if not os.path.exists("/usr/local/bin/fn"):
        # It does not, let's ask to install!
        menu_install_fractal(network, region)

    # Can this user access docker and is our container up?
    if check_container_running(config.container_name):

        # Print Loading
        print("* Gathering Validator Information... ")
        print_stars()

        # Init parser for extra flags:
        parser = argparse.ArgumentParser(
            description="Fractal Validator Toolbox - Help Menu"
        )
        parse_flags(parser, region, network)

        # Intro
        loader_intro()
        print_stars()
        print("* Loading Validator Menu...")

        # fn is found, is the fractal container running? Run the 'docker ps' command and filter the output using 'grep'

        backup_folder_check()
        run_findora_menu()
    else:
        # fn found, container not online, run troubleshooting process
        run_troubleshooting_process()


if __name__ == "__main__":
    while True:
        main()
