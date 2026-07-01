import csv

# Explicit removals based on User Feedback (Batch 3)
EXPLICIT_REMOVALS = {
    '3131 CLIME RD',
    '3431 CLIME RD',
    '2584 BRIGGS RD',
    '1137 BROWN RD',
    '897 BROWN RD',
    '1520 BROWN RD',
    '1780 BROWN RD',
    '749 BROWN RD',
    '2439 LINDBERGH DR',
    '2421 LINDBERGH DR'
}

input_file = 'addresses_43223_formatted.csv'
output_file = 'addresses_43223_formatted_final_v4.csv'

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
            # Using startswith to catch the address and any potential unit suffixes.
            # Adding comma check for safety.
            if upper_line.startswith(removal + ",") or upper_line.startswith(removal + " "):
                keep = False
                break
            # Special case for exact match if line is just the address
            if upper_line == removal:
                keep = False
                break
        
        if keep:
            f_out.write(line + '\n')
            kept_count += 1
        else:
            removed_count += 1

print(f"Batch 3 Scrub Complete.")
print(f"Kept: {kept_count}")
print(f"Removed: {removed_count}")
