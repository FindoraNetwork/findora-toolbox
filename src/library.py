import subprocess
import os
import dotenv
import shutil
from os import environ
from colorama import Fore, Back, Style
from subprocess import PIPE, run
from toolbox.library import printStars, printStarsReset, return_txt, loadVarFile, disk_partitions, convertedUnit, freeSpaceCheck
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
    printStars()
    print(f'* Coming soon!')
    printStars()
    input("* Press ENTER to continue.")

def check_balance_menu() -> None:
    printStars()
    print(f'* Coming soon!')
    printStars()
    input("* Press ENTER to continue.")

def operating_system_updates() -> None:
    printStars()
    print(f'* Coming soon!')
    printStars()
    input("* Press ENTER to continue.")

def server_disk_check() -> None:
    printStarsReset()
    print("* Here are all of your mount points: ")
    for part in disk_partitions():
        print(part)
    printStars()
    total, used, free = shutil.disk_usage(ourDiskMount)
    total = str(convertedUnit(total))
    used = str(convertedUnit(used))
    print("Disk: " + str(ourDiskMount) + "\n" + freeSpaceCheck(validatorToolbox.our_disk_mount) + " Free\n" + used + " Used\n" + total + " Total")
    printStars()
    input("* Disk check complete, press ENTER to return to the main menu. ")

def coming_soon() -> None:
    printStars()
    print(f'* Coming soon!')
    printStars()
    input("* Press ENTER to continue.")

def menu_topper() -> None:
    Load1, Load5, Load15 = os.getloadavg()
    # get sign pct
    # get balances
    # get other validator data
    os.system("clear")
    printStars()
    print(f'{Style.RESET_ALL}* {Fore.GREEN}validator-toolbox for Findora FRA Validators by Easy Node   v{validatorToolbox.easy_version}{Style.RESET_ALL}   https://easynode.pro *')
    printStars()
    print(f'* Current disk space free: {Fore.CYAN}{freeSpaceCheck(validatorToolbox.our_disk_mount): >6}{Style.RESET_ALL}\n')
    printStars()
    print(f"* CPU Load Averages: {round(Load1, 2)} over 1 min, {round(Load5, 2)} over 5 min, {round(Load15, 2)} over 15 min")
    printStars()
    return
    

def run_findora_menu() -> None:
    menu_options = {
        1: refresh_stats,
        2: check_balance_menu,
        10: coming_soon,
        11: coming_soon,
        12: coming_soon,
        13: server_disk_check,
        15: allSysInfo,
        999: menuRebootServer,
    }
    while True:
        os.system("clear")
        menu_topper()
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