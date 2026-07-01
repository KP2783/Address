import csv
import re

# 1. Define Street Categories (for context, though we keep most)
# We will use these to be extra safe, but our logic is primarily keyword-based now.

def get_street(address):
    parts = address.split(',')
    if len(parts) >= 1:
        street_part = parts[0].strip()
        match = re.search(r'^\d+\s+(.*)', street_part)
        if match:
            return match.group(1).strip().upper()
        return street_part.strip().upper()
    return ""

input_file = 'addresses_43223_formatted.csv'
output_file = 'addresses_43223_formatted_cleaned.csv'

kept_count = 0
removed_count = 0

with open(input_file, 'r') as f_in, open(output_file, 'w', newline='') as f_out:
    # Copy header
    header = f_in.readline()
    f_out.write(header)
    
    for line in f_in:
        line = line.strip()
        if not line:
            continue
            
        upper_line = line.upper()
        
        keep = True
        
        # 1. Remove Explicit Commercial Keywords
        # "UNIT GMB" and "UNIT PAV" were found to be hospital units.
        if " SUITE " in upper_line or " STE " in upper_line or " OFFICE " in upper_line or " BLDG " in upper_line:
            keep = False
        elif " UNIT GMB" in upper_line or " UNIT PAV" in upper_line:
            keep = False
            
        # 2. Remove Specific Known Commercial Addresses
        # 2200 W Broad St is Central Ohio Behavioral Healthcare
        if "2200 W BROAD ST" in upper_line:
            keep = False
            
        # 3. Keep everything else
        # We verified that "Briggs Center Dr", "Western Hill Ct", "Campbell Ave" (Round #) are residential.
        # We verified "2051 Sullivant Ave Unit B" is residential.
        # So we do not remove based on "Unit" or "Center Dr" or "Round Numbers".
        
        if keep:
            f_out.write(line + '\n')
            kept_count += 1
        else:
            removed_count += 1

print(f"Processing Complete.")
print(f"Kept: {kept_count}")
print(f"Removed: {removed_count}")
