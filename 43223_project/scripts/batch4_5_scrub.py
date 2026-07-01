import csv

# Explicit removals based on User Feedback (Batch 4 & 5)
# Includes commercial businesses, municipal facilities, and specific rental properties identified by user.

EXPLICIT_REMOVALS_EXACT = {
    '1209 BROWN RD',
    '1400 BROWN RD',
    '1300 BROWN RD',
    '1730 BROWN RD',
    '1738 BROWN RD',
    '1053 BROWN RD',
    '1815 BROWN RD',
    '741 BROWN RD',
    '2801 CLIME RD',
    '2565 CLIME RD',
    '3231 CLIME RD',
    '3329 CLIME RD',
    '3118 CLIME RD',
    '3030 CLIME RD',
    '2501 JACKSON PIKE',
    '1622 PEABODY AVE',
    '595 VAN BUREN DR',
    '1701 THOMAS AVE',
    '200 DAKOTA AVE',
    '2268 WHITEHEAD RD',
    '3600 HIGH CREEK DR',
    '3570 HIGH CREEK DR',
    '2253 AUTUMN VILLAGE CT',
    '583 S HIGHLAND AVE',
    '19 S HIGHLAND AVE',
    '2157 W MOUND ST',
    '1155 W MOUND ST',
    '1759 W MOUND ST',
    '1127 WOODBROOK CIR W',
    '1149 WOODBROOK CIR W',
    '2358 WOODBROOK CIR S K',
    '2357 WOODBROOK CIR S A',
    '769 CANONBY PL B',
    '750 CANONBY PL 2H',
    '773 CANONBY PL 2F',
    '731 CANONBY PL B',
    '781 CANONBY PL 3H',
    '881 EATON AVE A',
    '415 NACE AVE UNIT A',
    '860 GREENFIELD DR 2G',
    '891 GREENFIELD DR 1B',
    '1670 HARRISBURG PIKE APT 2K',
    '2557 CLIME RD',
    '2669 CLIME RD',
    '2558 BRIGGS RD',
    '2562 BRIGGS RD',
    '2171 FRANK RD APT R',
    '1371 BROWN RD UNIT D',
    '1592 GARLING AVE APT REA',
    '2415 LINDBERGH DR'
}

# For 650 Van Buren Dr, the user identified it as a facility (Van Buren Village/Shelter).
# We should remove all units associated with this address.
PREFIX_REMOVALS = {
    '650 VAN BUREN DR'
}

input_file = 'addresses_43223_formatted.csv'
output_file = 'addresses_43223_formatted_final_v5.csv'

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
        
        # Check Exact Removals (allowing for comma/space suffix to ensure full word match)
        for removal in EXPLICIT_REMOVALS_EXACT:
            # We want to match the address part. 
            # If the line starts with the removal and is followed by a comma or space, it's a match.
            # Or if it's an exact match.
            if upper_line == removal or upper_line.startswith(removal + ",") or upper_line.startswith(removal + " "):
                keep = False
                break
        
        # Check Prefix Removals
        if keep:
            for removal in PREFIX_REMOVALS:
                if upper_line.startswith(removal):
                    keep = False
                    break
        
        if keep:
            f_out.write(line + '\n')
            kept_count += 1
        else:
            removed_count += 1
            # print(f"Removed: {line}")

print(f"Batch 4 & 5 Scrub Complete.")
print(f"Kept: {kept_count}")
print(f"Removed: {removed_count}")
