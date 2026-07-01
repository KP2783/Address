import csv
import re

# 1. Define Street Categories
RESIDENTIAL_STREETS = {
    'WHITETHORNE AVE', 'COLUMBIAN AVE', 'CLIME RD', 'BROWN RD', 'BELVIDERE AVE', 
    'MIDLAND AVE', 'CLARENDON AVE', 'S HIGHLAND AVE', 'WREXHAM AVE', 'NASHOBA AVE', 
    'LITTLE AVE', 'THOMAS AVE', 'BELLOWS AVE', 'LECHNER AVE', 'BUTLER AVE', 
    'MARSDALE AVE', 'WOODBROOK CIR W', 'WOODBROOK CIR N', 'WOODBROOK LN', 
    'HOPKINS AVE', 'WEST PARK AVE', 'DAKOTA AVE', 'CAMPBELL AVE', 'WOODBURY AVE', 
    'TOWNSEND AVE', 'LARCOMB AVE', 'GENEVA AVE', 'S YALE AVE', 'SAFFORD AVE', 
    'HILLTONIA AVE', 'S CENTRAL AVE', 'HART RD', 'VAUGHN ST', 'S PRINCETON AVE', 
    'RICHMOND RD', 'AVONDALE AVE', 'UNION AVE', 'ROCKY RD', 'DANA AVE', 
    'BIG TREE DR', 'FAIRMONT AVE', 'RIVER BEND RD', 'SOUTHWEST BLVD', 'DEMOREST RD'
}

MIXED_STREETS = {
    'SULLIVANT AVE', 'W MOUND ST', 'HARRISBURG PIKE', 'W RICH ST', 
    'FRANK RD', 'HARMON AVE', 'EAKIN RD', 'W BROAD ST'
}

# 2. Load Business Patterns (Round Numbers & Keywords)
commercial_patterns = set()
try:
    with open('business_patterns_43223.txt', 'r') as f:
        for line in f:
            line = line.strip()
            if ',' in line:
                # Store the full address string for exact matching
                commercial_patterns.add(line.upper())
except FileNotFoundError:
    print("Warning: business_patterns_43223.txt not found. Skipping pattern check.")

def get_street(address):
    parts = address.split(',')
    if len(parts) >= 1:
        street_part = parts[0].strip()
        match = re.search(r'^\d+\s+(.*)', street_part)
        if match:
            return match.group(1).strip().upper()
        return street_part.strip().upper()
    return ""

input_file = 'addresses_43223_formatted.csv'
output_file = 'addresses_43223_formatted_cleaned.csv'

kept_count = 0
removed_count = 0

with open(input_file, 'r') as f_in, open(output_file, 'w') as f_out:
    # Copy header
    header = f_in.readline()
    f_out.write(header)
    
    for line in f_in:
        line = line.strip()
        if not line:
            continue
            
        upper_line = line.upper()
        street = get_street(line)
        
        keep = True
        reason = ""
        
        # 1. Check Explicit Commercial Keywords (Global)
        if " SUITE " in upper_line or " STE " in upper_line or " OFFICE " in upper_line or " BLDG " in upper_line:
            keep = False
            reason = "Commercial Keyword"
            
        # 2. Check Business Patterns List
        if keep and upper_line in commercial_patterns:
            keep = False
            reason = "Business Pattern List"
            
        # 3. Street-Specific Logic
        if keep:
            if street in RESIDENTIAL_STREETS:
                keep = True # High confidence residential
            elif street in MIXED_STREETS:
                # Mixed Street Logic
                if " APT " in upper_line or " UNIT " in upper_line or " REAR " in upper_line or " 1/2 " in upper_line:
                    keep = True # Likely residential unit
                else:
                    # Simple address on mixed street.
                    keep = True
            else:
                # Unknown street.
                # Assume residential.
                keep = True
                
        if keep:
            f_out.write(line + '\n')
            kept_count += 1
        else:
            removed_count += 1

print(f"Processing Complete.")
print(f"Kept: {kept_count}")
print(f"Removed: {removed_count}")
