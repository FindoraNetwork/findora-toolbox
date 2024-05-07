from toolbox import get_fn_values, process_fn_stats
import sys
import json

print('* Getting fn stats... ', end='', flush=True)
output = get_fn_values()
print('Completed', flush=True)

print('* Compiling fn information... ', end='', flush=True)
findora_validator_stats, validator_address, public_address = process_fn_stats(output)
findora_validator_stats_str = json.dumps(findora_validator_stats, indent=4)
print('Completed', flush=True)

print('* findora_validator_stats:', findora_validator_stats_str)
print('* validator_address:', validator_address)
print('* public_address:', public_address)
