import requests
import json
import web3
import re
import subprocess
from datetime import datetime, timezone
from library import capture_stats, findora_gwei_convert
from pprint import pprint
from decimal import Decimal

# This is just a script for testing stuff, will print out stats currently.
def get_fn_stats():
    output = subprocess.check_output(["fn", "show"])
    json_string = output.decode().replace("b'", "").replace("\x1b[31;01m", "").replace("\x1b[00m", "")

    lines = json_string.split("\n")

    print(lines)

    fn_info = {}
    if int(lines[17].split()[1][:-1]) == 0:
        fn_info["Network"] = lines[1]
        fn_info["Current Block"] = lines[29].split()[1][:-1]
        fn_info["Balance"] = f"{'{:,}'.format(round(findora_gwei_convert(int(lines[10].split()[0])), 2))} FRA"
    else:
        fn_info["Network"] = lines[1]
        fn_info["Current Block"] = lines[34].split()[1][:-1]
        fn_info["Proposed Blocks"] = lines[36].split()[1]
        fn_info["Self Delegation"] = f"{'{:,}'.format(round(findora_gwei_convert(int(lines[17].split()[1][:-1])), 2))} FRA"
        fn_info["Balance"] = f"{'{:,}'.format(round(findora_gwei_convert(int(lines[10].split()[0])), 2))} FRA"
        fn_info["Pool Unclaimed FRA"] = f"{'{:,}'.format(round(findora_gwei_convert(int(lines[51].split()[1][:-1])), 2))} FRA"
        fn_info["Server Rank"] = lines[45].split()[1][:-1]
        fn_info["Delegator Count"] = lines[66].split()[1]
        fn_info["Commission Rate"] = f"{int(lines[47][:-1])/100}%"

    for i in fn_info:
        spaces = "                                      "
        print(f"* {i}: {spaces[len(i):]}{fn_info[i]}")

    return fn_info

get_fn_stats()
    