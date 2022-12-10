import subprocess
import os
from colorama import Fore, Back, Style
from subprocess import PIPE, run
from toolbox.library import printStars, return_txt
from toolbox.toolbox import menuError
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

def run_findora_menu() -> None:
    while True:
        os.system("clear")
        menu_findora()
        try:
            option = int(input("* Enter your option: "))
        except ValueError:
            menuError()
            menu_findora()