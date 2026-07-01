
import sys
import os
import re

# Add scripts dir to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from extract_streets import extract_streets
from process_mega_batch_results import STREET_MAP, EXCLUDED_STREET_NAMES

INPUT_BATCH_FILE = 'output/current_mega_batch.txt'

def main():
    unique_streets = extract_streets(INPUT_BATCH_FILE)
    new_streets = set()
    
    for s in unique_streets:
        # Check explicit map
        if s in STREET_MAP: continue
        
        # Clean the street name for comparison
        address_part = s # Assuming 's' is the address part to clean
        if address_part:
            # Remove house number
            street_only = re.sub(r'^\d+\s+', '', address_part).strip()
            # Remove unit
            street_only = re.sub(r'\s+(UNIT|APT|STE|#).*$', '', street_only, flags=re.IGNORECASE)
            # Remove Gxx and BLDG
            street_only = re.sub(r'\sG\d+$', '', street_only)
            street_only = re.sub(r'\sBLDG\s?\d+$', '', street_only, flags=re.IGNORECASE)
            
            # Clean up city suffix if present
            street_only = street_only.split(' Hilliard')[0].split(' Columbus')[0]
            
            # Use the cleaned street_only for subsequent checks
            s_cleaned = street_only.upper().strip()
        else:
            s_cleaned = s.upper().strip()
        
        # Check if already processed (cleaned version)
        if s_cleaned in STREET_MAP: continue

        # Check excluded list (startswith logic)
        is_excl = False
        for ex in EXCLUDED_STREET_NAMES:
            if s_cleaned.startswith(ex): # Changed 's' to 's_cleaned'
                is_excl = True
                break
        if is_excl: continue
            
        new_streets.add(s_cleaned)
        
    for s in sorted(list(new_streets)):
        print(s)


if __name__ == "__main__":
    main()
