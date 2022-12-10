import subprocess
from subprocess import PIPE, run
from toolbox.library import printStars

def dockerCheck():
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
