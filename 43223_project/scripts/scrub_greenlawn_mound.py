import csv

# Explicit removals based on User Feedback and recent searches
# 766 Greenlawn Ave -> Columbus Monument Company
# 638 Greenlawn Ave -> Aggressive Mechanical Inc
# 1632 W Mound St -> Commercial Building
# 340 Greenlawn Ave -> Retail/Restaurant
# 555 Greenlawn Ave -> Mobile Home Park / Dealer (Mixed, but often commercial listing. Let's keep if residential units are listed, but remove the main address if it's just the park office/dealer. The list has "555 Greenlawn Ave" without unit. Safest to remove main address if it's the dealer.)
# 306 Greenlawn Ave -> Potential Commercial Garage (Auditor hint). Let's check if we have it.
# 0 Greenlawn Ave -> Invalid/Commercial Land

EXPLICIT_REMOVALS = {
    '766 GREENLAWN AVE',
    '638 GREENLAWN AVE',
    '1632 W MOUND ST',
    '340 GREENLAWN AVE',
    '555 GREENLAWN AVE',
    '0 GREENLAWN AVE',
    '306 GREENLAWN AVE'
}

input_file = 'addresses_43223_formatted.csv'
output_file = 'addresses_43223_formatted_scrubbed.csv'

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
        
        # 1. Check Explicit Removals
        for removal in EXPLICIT_REMOVALS:
            # Exact match on address part to avoid removing "555 Greenlawn Ave Lot 1" if it existed (though file seems to have just 555)
            # Actually, let's look at the file content for 555.
            # The grep showed "555 Greenlawn Ave, Columbus, OH 43223". No unit.
            if removal in upper_line:
                keep = False
                break
        
        if keep:
            f_out.write(line + '\n')
            kept_count += 1
        else:
            removed_count += 1
            # print(f"Removed: {line}")

print(f"Targeted Scrub Complete.")
print(f"Kept: {kept_count}")
print(f"Removed: {removed_count}")
