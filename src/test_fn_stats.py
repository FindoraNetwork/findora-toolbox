from toolbox import get_fn_values, process_fn_stats
import sys
import json

print('* Getting fn stats... ', end='', flush=True)
public_address, balance, server_url, delegation_info, validator_address_evm = (
    get_fn_values()
)
print('Completed', flush=True)

print('* Compiling fn information... ', end='', flush=True)
findora_validator_stats = process_fn_stats(
    validator_address_evm, balance, server_url, delegation_info
)
findora_validator_stats = json.dumps(findora_validator_stats, indent=4)
print('Completed', flush=True)

print('* findora_validator_stats:', findora_validator_stats)
print('* validator_address:', validator_address_evm)
print('* public_address:', public_address)
