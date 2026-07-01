import csv

# Final Batch of Removals
# User Provided:
# 3500 Clime Rd
# 1327 Brown Rd
# 1459 Harrisburg Pike (and units)
# 1285 Brown Rd
# 2500 Clime Rd
# 2590 Clime Rd

# Proactively Identified:
# 1270 Brown Rd (Commercial Zoning)
# 1660 Brown Rd (Commercial/Ambiguous Multi-unit)
# 2540 Clime Rd (Vacant Land)
# 2595 Clime Rd (Vacant Land)
# 1280 Brown Rd (Commercial/Fast Food)

EXPLICIT_REMOVALS = {
    '3500 CLIME RD',
    '1327 BROWN RD',
    '1459 HARRISBURG PIKE',
    '1285 BROWN RD',
    '2500 CLIME RD',
    '2590 CLIME RD',
    '1270 BROWN RD',
    '1660 BROWN RD',
    '2540 CLIME RD',
    '2595 CLIME RD',
    '1280 BROWN RD'
}

input_file = 'addresses_43223_formatted.csv'
output_file = 'addresses_43223_formatted_final_v2.csv'

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
        
        keep = True
        
        for removal in EXPLICIT_REMOVALS:
            # Check for address match. 
            # We want to remove "1459 Harrisburg Pike" AND "1459 Harrisburg Pike Apt A"
            # So startswith is appropriate.
            if upper_line.startswith(removal):
                keep = False
                break
        
        if keep:
            f_out.write(line + '\n')
            kept_count += 1
        else:
            removed_count += 1

print(f"Final Batch Scrub Complete.")
print(f"Kept: {kept_count}")
print(f"Removed: {removed_count}")
