
import sys
import os
sys.path.append('scripts')
from batch_validate_43026 import load_addresses, get_processed_addresses

def debug_counts():
    print("Loading all addresses...")
    all_addrs = load_addresses()
    print(f"Total Source: {len(all_addrs)}")
    
    unique_source = set(a['address'] for a in all_addrs)
    print(f"Total Unique Source: {len(unique_source)}")
    
    print("Getting processed...")
    processed = get_processed_addresses()
    print(f"Total Processed: {len(processed)}")
    
    remaining = [a['address'] for a in all_addrs if a['address'] not in processed]
    print(f"Remaining Raw: {len(remaining)}")
    
    remaining_unique = set(remaining)
    print(f"Remaining Unique: {len(remaining_unique)}")
    
    if len(remaining) > 0:
        print("First 10 remaining:")
        for r in remaining[:10]:
            print(r)

if __name__ == "__main__":
    debug_counts()
