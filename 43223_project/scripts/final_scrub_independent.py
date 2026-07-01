import csv

# Final Independent Scrub
# Removes ONLY confirmed commercial businesses.
# Strictly PRESERVES residential apartments and rentals.

CONFIRMED_COMMERCIAL_REMOVALS = {
    '1209 BROWN RD', # Subway
    '1400 BROWN RD', # Dairy Mart
    '1300 BROWN RD', # Commercial/BMV reported
    '1730 BROWN RD', # Auto Service
    '1738 BROWN RD', # Auto Sales
    '1053 BROWN RD', # Restaurant
    '1815 BROWN RD', # Dairy Mart
    '2801 CLIME RD', # Family Dollar
    '2565 CLIME RD', # Shell Station
    '3231 CLIME RD', # Enterprise Rent-A-Car
    '3329 CLIME RD', # BP Station
    '3118 CLIME RD', # Retail
    '3030 CLIME RD', # Friends Worship Center (Church)
    '2501 JACKSON PIKE', # Landfill/Transfer Station
    '1622 PEABODY AVE', # Church
    '595 VAN BUREN DR', # Shelter (Institutional)
    '1701 THOMAS AVE', # Small Business
    '3600 HIGH CREEK DR', # School
    '3570 HIGH CREEK DR', # Drywall LLC
    '583 S HIGHLAND AVE', # Window Tint
    '19 S HIGHLAND AVE', # Auto Repair
    '1155 W MOUND ST', # Under The Big Top
    '1759 W MOUND ST', # AEP
    '1281 SULLIVANT AVE', # Restoration
    '1137 APPLE BLOSSOM LN', # OSU
    '1709 THOMAS AVE', # Thomas Center
    '230 MIDLAND AVE', # Auto
    '445 S GLENWOOD AVE', # Auto
    '1945 FAIRMONT AVE', # Dental
    '1503 WALSH AVE', # Auto Body
    '1559 THOMAS AVE', # Thomas Center
    '495 BUTLER AVE', # Auto
    '1000 CAMPBELL AVE', # Auto
    '540 CATHERINE ST', # Cafe
    '3550 ROCKY RD' # Storage
}

input_file = 'addresses_43223_formatted.csv'
output_file = 'addresses_43223_formatted_final_v8.csv'

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
        
        for removal in CONFIRMED_COMMERCIAL_REMOVALS:
            # Check for address match.
            # Using startswith to catch the address and any potential unit suffixes.
            # Adding comma check for safety.
            if upper_line.startswith(removal + ",") or upper_line.startswith(removal + " ") or upper_line == removal:
                keep = False
                break
        
        if keep:
            f_out.write(line + '\n')
            kept_count += 1
        else:
            removed_count += 1

print(f"Final Independent Scrub Complete.")
print(f"Kept: {kept_count}")
print(f"Removed: {removed_count}")
