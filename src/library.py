import subprocess
import os
from colorama import Fore, Back, Style
from subprocess import PIPE, run
from toolbox.library import printStars, return_txt, freeSpaceCheck, serverDriveCheck
from toolbox.toolbox import menuError, menuUbuntuUpdates, menuRebootServer, finish_node
from toolbox.allsysinfo import allSysInfo
from config import validatorToolbox

def docker_check():
    status = subprocess.call(["docker"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if status == 0:
        print("* Docker is available and working properly.")
        print("* Menu coming soon!")
        printStars()
        return 0
    else:
        print("* Docker is not available or is not working properly.")
        print("* Install docker on this server and give the user access to continue.")
        printStars()
        raise SystemExit(0)

def menu_findora() -> None:
    # menuTopperFull()
    for x in return_txt(validatorToolbox.findora_menu):
        x = x.strip()
        try:
            x = eval(x)
        except SyntaxError:
            pass
        if x:
            print(x)

def refresh_stats() -> None:
    print(f'* Coming soon!')
    printStars()

def check_balance_menu() -> None:
    print(f'* Coming soon!')
    printStars()

def operating_system_updates() -> None:
    print(f'* Coming soon!')
    printStars()

def server_disk_check() -> None:
    print(f'* Coming soon!')
    printStars()

def coming_soon() -> None:
    print(f'* Coming soon!')
    printStars()

def run_findora_menu() -> None:
    menu_options = {
        1: refresh_stats,
        2: check_balance_menu,
        12: menuUbuntuUpdates,
        13: server_disk_check,
        14: coming_soon,
        15: allSysInfo,
        999: menuRebootServer,
    }
    while True:
        os.system("clear")
        menu_findora()
        try:
            option = int(input("* Enter your option: "))
        except ValueError:
            menuError()
            menu_findora()
        if option == 0:
            return finish_node()
        os.system("clear")
        menu_options[option]()