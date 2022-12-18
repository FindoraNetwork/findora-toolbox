import requests
import json
import web3
from datetime import datetime, timezone
from library import capture_stats
from pprint import pprint
from decimal import Decimal

now = datetime.now(timezone.utc)

response = requests.get("http://localhost:26657/status")
stats = json.loads(response.text)

def convert(findora):
    fra_amount = int(findora) / 1000000
    return fra_amount

fra = convert(stats['result']['validator_info']['voting_power'])

print(f"* Address:           {stats['result']['validator_info']['address']}")
print(f"* Current Stake:     {'{:,}'.format(round(fra, 2))} FRA")
print(f"* Catching Up:       {stats['result']['sync_info']['catching_up']}")
print(f"* Latest Block:      {stats['result']['sync_info']['latest_block_height']}")
print(f"* Latest Block Time: {stats['result']['sync_info']['latest_block_time'][:-11]}")
print(f"* Current Time UTC:  {now.strftime('%Y-%m-%dT%H:%M:%S')}")
