import csv

input_file = 'addresses_43223_formatted.csv'
output_file = 'addresses_43223_formatted_cleaned.csv'
removed_file = 'addresses_43223_removed_review.csv'

# 1. Suspicious Street Names
REMOVE_STREETS = ['BRIGGS CENTER DR']

# 2. Specific Suspicious Units
REMOVE_EXACT_UNITS = {
    '1291 W Mound St Unit Grge',
    '1709 Frank Rd Unit Vngr',
    '862 Frank Rd Unit S-2'
}

# 3. Broad Street Units
REMOVE_BROAD_ST_UNITS = {
    '1600 W Broad St Unit A', '1600 W Broad St Unit E', '1600 W Broad St Unit F',
    '1600 W Broad St Unit G', '1600 W Broad St Unit H', '1600 W Broad St Unit I',
    '1600 W Broad St Unit J', '1600 W Broad St Unit K',
    '1606 W Broad St Unit D',
    '1610 W Broad St Unit B',
    '1620 W Broad St Unit C'
}

# 4. Briggs Rd (Non-Unit) - From the review list
# I will load these dynamically or just hardcode the ones I saw if I can't read the file easily in the script.
# Better to read the review_candidates file if it exists, but I'll just hardcode the logic to match the "Mixed Streets (Non-Unit)" section for Briggs Rd.
# Actually, I'll just list them here based on the previous `cat` output to be safe and precise.
REMOVE_BRIGGS_RD = {
    '2520 Briggs Rd', '2512 Briggs Rd', '2594 Briggs Rd', '2530 Briggs Rd', '2590 Briggs Rd',
    '2538 Briggs Rd', '2516 Briggs Rd', '2558 Briggs Rd', '2562 Briggs Rd', '2555 Briggs Rd',
    '2293 Briggs Rd', '2350 Briggs Rd', '2330 Briggs Rd', '2719 Briggs Rd', '2337 Briggs Rd',
    '2751 Briggs Rd', '2339 Briggs Rd', '2735 Briggs Rd', '2300 Briggs Rd', '2707 Briggs Rd',
    '2727 Briggs Rd', '2402 Briggs Rd', '2478 Briggs Rd', '2400 Briggs Rd', '2699 Briggs Rd',
    '2691 Briggs Rd', '2683 Briggs Rd', '2546 Briggs Rd', '2743 Briggs Rd', '2478 1/2 Briggs Rd',
    '2651 Briggs Rd', '2405 Briggs Rd', '2563 Briggs Rd', '2602 Briggs Rd'
}

removed_count = 0
kept_count = 0

with open(input_file, 'r') as f_in, \
     open(output_file, 'w', newline='') as f_out, \
     open(removed_file, 'w', newline='') as f_rem:
    
    reader = csv.DictReader(f_in)
    fieldnames = reader.fieldnames
    
    writer = csv.DictWriter(f_out, fieldnames=fieldnames)
    writer.writeheader()
    
    rem_writer = csv.DictWriter(f_rem, fieldnames=fieldnames)
    rem_writer.writeheader()
    
    for row in reader:
        # Clean row of any keys not in fieldnames (like None from trailing commas)
        row = {k: v for k, v in row.items() if k in fieldnames}
        
        addr = row['address']
        upper_addr = addr.upper()
        
        should_remove = False
        
        # Check Street Names
        for street in REMOVE_STREETS:
            if street in upper_addr:
                should_remove = True
                break
        
        # Check Exact Units
        if not should_remove and addr in REMOVE_EXACT_UNITS:
            should_remove = True
            
        # Check Broad St Units
        if not should_remove and addr in REMOVE_BROAD_ST_UNITS:
            should_remove = True
            
        # Check Briggs Rd
        if not should_remove and addr in REMOVE_BRIGGS_RD:
            should_remove = True
            
        if should_remove:
            rem_writer.writerow(row)
            removed_count += 1
        else:
            writer.writerow(row)
            kept_count += 1

print(f"Finished processing.")
print(f"Kept: {kept_count}")
print(f"Removed: {removed_count}")
print(f"Cleaned file: {output_file}")
print(f"Removed addresses: {removed_file}")
