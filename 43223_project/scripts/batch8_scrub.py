import csv

# Batch 8 Independent Scrub
# Removes confirmed commercial businesses from User's Batch 8 list.
# Strictly PRESERVES residential homes (e.g., Cypress Ave, Glenwood Ave) even if flagged by user.

CONFIRMED_COMMERCIAL_REMOVALS = {
    '701 HARMON PLZ', # Fiber PRO
    '715 HARMON PLZ', # Hanson
    '702 HARMON PLZ',
    '2500 JACKSON PIKE', # Government/Industrial
    '2566 JACKSON PIKE',
    '2463 JACKSON PIKE',
    '2293 BRIGGS RD',
    '690 BROWN RD',
    '2350 BRIGGS RD', # Three-C Body Shops
    '2330 BRIGGS RD', # Life Changers Church
    '177 S CYPRESS AVE', # Steph's Way
    '187 S CYPRESS AVE', # Cypress Kitchen
    '718 HARMON PLZ',
    '693 HARMON PLZ',
    '1291 W MOUND ST UNIT GRGE', # Depot Connect
    '2683 BRIGGS RD',
    '685 HARMON PLZ',
    '694 HARMON PLZ',
    '1283 W TOWN ST',
    '704 HARMON PLZ',
    '1301 LITTLE ST',
    '2554 JACKSON PIKE',
    '1319 BRIGGS CENTER DR',
    '2546 BRIGGS RD',
    '599 AMERICAN BLVD',
    '661 S SOUDER AVE',
    '699 HARMON PLZ',
    '191 S CYPRESS AVE', # Cypress Kitchen
    '177 S HIGHLAND AVE',
    '1222 CAMPBELL AVE',
    '3200 CLIME RD',
    '1560 BERKHARD DR',
    '713 HARMON PLZ',
    '2104 JACKSON PIKE',
    '603 AMERICAN BLVD',
    '1300 LITTLE AVE',
    '675 HARMON PLZ'
}

# Prefix removals for Jackson Pike complex variants
PREFIX_REMOVALS = {
    '2500 JACKSON PIKE'
}

input_file = 'addresses_43223_formatted.csv'
output_file = 'addresses_43223_formatted_final_v9.csv'

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
        
        # Check Prefix Removals
        for removal in PREFIX_REMOVALS:
            if upper_line.startswith(removal):
                keep = False
                break

        if keep:
            for removal in CONFIRMED_COMMERCIAL_REMOVALS:
                # Check for address match.
                if upper_line.startswith(removal + ",") or upper_line.startswith(removal + " ") or upper_line == removal:
                    keep = False
                    break
        
        if keep:
            f_out.write(line + '\n')
            kept_count += 1
        else:
            removed_count += 1

print(f"Batch 8 Independent Scrub Complete.")
print(f"Kept: {kept_count}")
print(f"Removed: {removed_count}")
