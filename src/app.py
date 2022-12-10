import os
import subprocess
from subprocess import run
from toolbox.library import loaderIntro, printStars, askYesNo
from library import dockerCheck

# Check the status and print a message

if __name__ == "__main__":
    loaderIntro()
    printStars()
    dockerCheck()
    if os.path.exists('/usr/local/bin/fn') is False:
        # Run installer ya'll!
        print(f'* Welcome to EasyNode.PRO Validator Toolbox for Findora!')
        print(f"* We've detected that Docker is properly installed for this user, excellent!")
        print(f"* It doesn't look like you have Findora installed.")
        print(f"* We will setup Findora validator on this server with a brand new wallet and start syncing with the blockchain.")
        answer = askYesNo(f'* Do you want to install it now? (Y/N) ')
        if answer:
            subprocess.run('wget https://raw.githubusercontent.com/easy-node-pro/findora-validator-scripts/main/easy_install_mainnet.sh -O install_mainnet.sh && bash -x install_mainnet.sh')
            printStars()
            print(f'* Setup has completed. Once you are synced up (catching_up=False) you are ready to create your validator on-chain or migrate from another server onto this server.')
            raise SystemExit(0)
        printStars()
    else:
        # fn is found, is the container running?
        # Set the container name
        container_name = "findorad"

        # Run the 'docker ps' command and filter the output using 'grep'
        status = subprocess.call(["docker", "ps", "--filter", f"name={container_name}"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        # Check the status and print a message
        if status == 0:
            print(f"* The container '{container_name}' is running.")
        else:
            print(f"* The container '{container_name}' is not running.")
        printStars()


