import csv
import re

# 1. Load Suspects
suspect_addresses = set()
with open('commercial_suspects_43223.txt', 'r') as f:
    for line in f:
        line = line.strip()
        if ',' in line:
            # Store full upper case address
            suspect_addresses.add(line.upper())

# 2. Define Explicit Removals (found via search)
EXPLICIT_REMOVALS = {
    '1985 HARMON AVE',
    '2200 W BROAD ST'
}

input_file = 'addresses_43223_formatted.csv'
output_file = 'addresses_43223_formatted_strict.csv'

kept_count = 0
removed_count = 0

with open(input_file, 'r') as f_in, open(output_file, 'w', newline='') as f_out:
    header = f_in.readline()
    f_out.write(header)
    
    for line in f_in:
        line = line.strip()
        if not line:
            continue
            
        upper_line = line.upper()
        addr_part = line.split(',')[0].strip().upper() # "123 STREET"
        
        keep = True
        reason = ""
        
        # 1. Commercial Keywords
        if " SUITE " in upper_line or " STE " in upper_line or " OFFICE " in upper_line or " BLDG " in upper_line:
            keep = False
            reason = "Commercial Keyword"
            
        # 2. Explicit Removals
        if keep:
            for removal in EXPLICIT_REMOVALS:
                if removal in upper_line:
                    keep = False
                    reason = "Explicit Removal"
                    break
        
        # 3. Suspect List Logic
        # If in suspect list AND NO residential unit indicator -> Remove
        if keep and upper_line in suspect_addresses:
            if " APT " in upper_line or " UNIT " in upper_line or " REAR " in upper_line or " 1/2 " in upper_line:
                keep = True # Keep suspect apartments
            else:
                keep = False # Remove suspect ambiguous (likely commercial/vacant on mixed street)
                reason = "Suspect List (No Unit)"
                
        if keep:
            f_out.write(line + '\n')
            kept_count += 1
        else:
            removed_count += 1
            # print(f"Removed: {line} ({reason})")

print(f"Strict Processing Complete.")
print(f"Kept: {kept_count}")
print(f"Removed: {removed_count}")
