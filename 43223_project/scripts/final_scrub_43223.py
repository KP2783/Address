import csv

# Explicit removals based on "Expert Review" (Google Search)
# 2079 Frank Rd -> Babbitt Bearing Co
# 1660 Frank Rd -> Ambiguous/Potential Commercial
# 733 Harrisburg Pike -> Restaurant (Downtown Tabby's)
# 1985 Harmon Ave -> Commercial
# 2200 W Broad St -> Hospital
# 2120 Eakin Rd -> Residential (Keep)
# 1644 Frank Rd -> Residential (Keep)
# 1198 Harmon Ave -> Residential (Keep)

EXPLICIT_REMOVALS = {
    '2079 FRANK RD',
    '1660 FRANK RD',
    '733 HARRISBURG PIKE',
    '1985 HARMON AVE',
    '2200 W BROAD ST'
}

input_file = 'addresses_43223_formatted.csv'
output_file = 'addresses_43223_formatted_final.csv'

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
            if removal in upper_line:
                keep = False
                break
        
        if keep:
            f_out.write(line + '\n')
            kept_count += 1
        else:
            removed_count += 1

print(f"Final Scrub Complete.")
print(f"Kept: {kept_count}")
print(f"Removed: {removed_count}")
