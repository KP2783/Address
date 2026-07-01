import csv

# Explicit removals based on User Feedback (Batch 7)
# Includes extensive list of businesses and apartments.

EXPLICIT_REMOVALS = {
    '1281 SULLIVANT AVE UNIT D',
    '1137 APPLE BLOSSOM LN',
    '1709 THOMAS AVE',
    '230 MIDLAND AVE',
    '445 S GLENWOOD AVE',
    '1945 FAIRMONT AVE',
    '1503 WALSH AVE',
    '1559 THOMAS AVE',
    '495 BUTLER AVE',
    '1000 CAMPBELL AVE',
    '540 CATHERINE ST',
    '891 EATON AVE A',
    '1511 STIMMEL RD UNIT 1B',
    '881 EATON AVE',
    '630 MINER AVE C',
    '365 S YALE AVE',
    '938 EATON AVE',
    '2179 W MOUND ST',
    '1520 MARSDALE AVE',
    '1420 OLD HICKORY DR',
    '619 CLARK AVE',
    '2268 WHITEHEAD RD',
    '3030 CLIME RD',
    '3260 RIVERPOINT CT',
    '550 CLARK AVE',
    '860 GREENFIELD DR',
    '891 GREENFIELD DR',
    '265 DAKOTA AVE',
    '750 CANONBY PL',
    '1712 RIPPLE BROOK RD',
    '1853 SCOTT VALLEY DR',
    '773 CANONBY PL',
    '781 CANONBY PL',
    '1583 TALL MEADOWS DR',
    '1261 WOODBROOK CIR W',
    '148 BELVIDERE AVE',
    '497 BELVIDERE AVE',
    '791 GRIGGS AVE',
    '1659 GREENVILLE RD',
    '324 LECHNER AVE',
    '2246 AUTUMN VILLAGE CT',
    '805 BELLOWS AVE',
    '686 HARMON PLZ',
    '2230 HOMEWOOD AVE',
    '3550 ROCKY RD',
    '1434 UNION AVE',
    '1453 PINESTONE DR',
    '3634 BROOKLINE AVE',
    '665 S SOUDER AVE',
    '3214 VALLEYWOOD DR',
    '650 VAN BUREN DR',
    '588 MINER AVE',
    '1537 RIVER BEND RD',
    '1520 BERKHARD DR',
    '951 FOREST CREEK DR E',
    '1513 STIMMEL RD',
    '1447 STIMMEL RD',
    '1281 SULLIVANT AVE',
    '2027 GREAT BROOK DR',
    '1643 FARBERDALE DR',
    '1731 WESTMEADOW DR',
    '200 DAKOTA AVE',
    '1155 W MOUND ST',
    '1670 HARRISBURG PIKE'
}

input_file = 'addresses_43223_formatted.csv'
output_file = 'addresses_43223_formatted_final_v7.csv'

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
            if upper_line.startswith(removal + ",") or upper_line.startswith(removal + " ") or upper_line == removal:
                keep = False
                break
        
        if keep:
            f_out.write(line + '\n')
            kept_count += 1
        else:
            removed_count += 1

print(f"Batch 7 Scrub Complete.")
print(f"Kept: {kept_count}")
print(f"Removed: {removed_count}")
