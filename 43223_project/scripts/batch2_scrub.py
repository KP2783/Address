import csv

# Explicit removals based on User Feedback (Batch 2)
EXPLICIT_REMOVALS = {
    '2581 CLIME RD',
    '2641 CLIME RD',
    '2588 BRIGGS RD',
    '759 BROWN RD',
    '1005 BROWN RD',
    '1380 EMIG RD',
    '1360 LOUVAINE DR',
    '2506 FRANKLIN AVE',
    '2421 1/2 LINDBERGH DR',
    '2052 WHITEHEAD RD',
    '802 BROWN RD',
    '810 BROWN RD'
}

input_file = 'addresses_43223_formatted.csv'
output_file = 'addresses_43223_formatted_final_v3.csv'

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
            # Using startswith to catch the address and any potential unit suffixes if they weren't caught by the grep
            # (though the grep showed exact matches mostly).
            # Also adding a comma check to be safe against partial number matches (e.g. 802 vs 8020)
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

print(f"Batch 2 Scrub Complete.")
print(f"Kept: {kept_count}")
print(f"Removed: {removed_count}")
