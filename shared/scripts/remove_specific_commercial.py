import csv

# Explicit removals based on User Feedback
EXPLICIT_REMOVALS = {
    '1285 BROWN RD',
    '1275 BROWN RD',
    '2500 CLIME RD',
    '2590 CLIME RD',
    '332 GREENLEAF RD'
}

input_file = 'addresses_43223_formatted.csv'
output_file = 'addresses_43223_formatted_cleaned.csv'

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
        
        # Check Explicit Removals
        for removal in EXPLICIT_REMOVALS:
            # Check if the removal address is in the line
            # We need to be careful not to match partials incorrectly, but these are full street numbers and names.
            # A simple substring check might be risky if there was "11285 Brown Rd", but let's check exact start or comma.
            # Given the format "1285 Brown Rd, Columbus...", a startswith check or check for "1285 Brown Rd," is safer.
            
            # Construct the check string to be safer
            check_str = removal + ","
            if upper_line.startswith(removal + ",") or upper_line.startswith(removal + " "):
                 keep = False
                 break
        
        if keep:
            f_out.write(line + '\n')
            kept_count += 1
        else:
            removed_count += 1
            # print(f"Removed: {line}")

print(f"User Feedback Scrub Complete.")
print(f"Kept: {kept_count}")
print(f"Removed: {removed_count}")
