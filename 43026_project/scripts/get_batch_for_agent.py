
import sys
import os

# Add local directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from batch_validate_43026 import get_next_batch

# Get next 2000 items
from batch_validate_43026 import get_processed_addresses, load_addresses

processed = get_processed_addresses()
# debug prints removed for cleaner output

batch = get_next_batch(batch_size=2000)
print("BATCH_START")
for addr in batch:
    print(addr)
print("BATCH_END")
