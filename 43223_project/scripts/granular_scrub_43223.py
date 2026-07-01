import csv
import re

# High Risk Streets where "Non-Unit" addresses are likely commercial
RISK_STREETS = {
    'SULLIVANT AVE', 'HARRISBURG PIKE', 'GREENLAWN AVE', 'W BROAD ST', 
    'STIMMEL RD', 'MCKINLEY AVE', 'CENTRAL AVE', 'W MOUND ST', 
    'W RICH ST', 'FRANK RD', 'HARMON AVE', 'EAKIN RD'
}

input_file = 'addresses_43223_formatted.csv'
output_file = 'addresses_43223_formatted_granular.csv'

kept_count = 0
removed_count = 0

def is_unit(address):
    upper = address.upper()
    # Check for explicit unit indicators
    if " APT " in upper or " UNIT " in upper or " # " in upper or " BLDG " in upper:
        return True
    # Check for patterns like " D31", " B15" at end
    if re.search(r'\s[A-Z]\d+$', upper): return True
    if re.search(r'\s\d+[A-Z]$', upper): return True
    if re.search(r'\s[A-Z]$', upper): return True
    return False

def get_street(address):
    parts = address.split(',')
    if len(parts) >= 1:
        street_part = parts[0].strip()
        match = re.search(r'^\d+\s+(.*)', street_part)
        if match:
            return match.group(1).strip().upper()
        return street_part.strip().upper()
    return ""

with open(input_file, 'r') as f_in, open(output_file, 'w', newline='') as f_out:
    header = f_in.readline()
    f_out.write(header)
    
    for line in f_in:
        line = line.strip()
        if not line:
            continue
            
        upper_line = line.upper()
        street = get_street(line)
        
        keep = True
        
        # Check if street is in Risk List
        is_risk_street = False
        for rs in RISK_STREETS:
            if rs in street: # Substring match to catch "S CENTRAL AVE"
                is_risk_street = True
                break
        
        if is_risk_street:
            # If on risk street, ONLY keep if it looks like a unit/apartment
            if not is_unit(line):
                keep = False
        
        if keep:
            f_out.write(line + '\n')
            kept_count += 1
        else:
            removed_count += 1

print(f"Granular Scrub Complete.")
print(f"Kept: {kept_count}")
print(f"Removed: {removed_count}")
