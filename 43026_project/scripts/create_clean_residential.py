import re

# 1. Load Suspect Addresses
suspect_addresses = set()
with open('commercial_corridor_review.txt', 'r') as f:
    for line in f:
        line = line.strip()
        if ',' in line:
            # Key is the "NUMBER STREET" part
            key = line.split(',')[0].strip().upper()
            suspect_addresses.add(key)

# 2. Define Lists
CONFIRMED_RESIDENTIAL = {
    'SINGLETON DR', 'STONEYBROOK BLVD', 'BLUEMONT PK', 'FISHINGER MILL DR', 
    'RIDGEBURY DR', 'RAVENNA LOOP', 'BENNIGAN DR', 'BRIDLE CREEK WAY', 
    'BLUEBIRD PL', 'SEDGE LN', 'BROOKLANDS DR', 'WOODLAND DR', 
    'MESSNER DR', 'RIDGEWOOD DR', 'PEPPER BERRY LN', 'BLUE LAGOON LN', 
    'VALENCIA PARK BLVD', 'QUARRY STONE DR', 'SCIOTO RUN BLVD', 
    'DARBYSHIRE DR', 'CRYSTAL CLEAR DR', 'DRAYTON RD', 
    'WHISPERING WILLOW LN', 'BENDING WILLOW LN', 'PAXTON DR', 'PAXTON DR S',
    'ORIOLE ST', 'CALICO CT', 'CABOT COVE DR', 'YAGGER BAY DR', 
    'HILLIARD STATION RD', 'BRAIDWOOD DR', 'HERITAGE LAKES DR', 
    'GREEN CLOVER DR', 'LAKEBRIDGE LN', 'CRYSTAL BALL DR', 'BAYRIDGE DR', 
    'GABLES LAKE DR', 'SILVERSTRAND DR', 'JASMINE LN', 'SPRINGDALE BLVD',
    'WINTERRINGER ST', 'GILLETTE AVE', 'DRIVEMERE RD'
}

REVIEW_STREETS = {
    'AVERY RD', 'BALDWIN RD', 'CAMERON RD', 'CEMETERY RD', 'CENTER ST', 
    'COSGRAY RD', 'DAVIDSON RD', 'DAVIS RD', 'DUBLIN RD', 'ELLIOTT RD', 
    'HAYDEN RUN RD', 'HIGH SCHOOL DR', 'JONES RD', 'KROEHLER DR', 
    'LEPPERT RD', 'MAIN ST', 'MORRIS RD', 'MUNICIPAL WAY', 'NORWICH ST', 
    'PATTERSON RD', 'ROBERTS RD', 'SCHIRTZINGER RD', 
    'SCIOTO DARBY CREEK RD', 'SMILEY RD', 'SPINDLER RD', 'TAYLOR LANE AVE', 
    'TRUEMAN BLVD', 'VETERANS MEMORIAL DR', 'WALKER RD',
    'SCIOTO DARBY RD', 'NIKE DR', 'LEAP CT', 'LEAP RD'
}

def get_street(address_line):
    # address_line is "123 STREET, City, OH, Zip"
    parts = address_line.split(',')
    if len(parts) >= 1:
        street_part = parts[0].strip()
        match = re.search(r'^\d+\s+(.*)', street_part)
        if match:
            return match.group(1).strip()
        return street_part.strip()
    return ""

input_file = 'addresses_43026_formatted.csv'
output_file = 'addresses_43026_residential_final.csv'

kept_count = 0
removed_count = 0

with open(input_file, 'r') as f_in, open(output_file, 'w') as f_out:
    # Read header
    header = f_in.readline()
    f_out.write(header)
    
    for line in f_in:
        line = line.strip()
        if not line:
            continue
            
        upper_line = line.upper()
        street = get_street(line)
        addr_key = line.split(',')[0].strip().upper()
        
        classification = "Unknown"
        
        # 1. Check Keywords
        if " SUITE " in upper_line or " STE " in upper_line:
            classification = "Commercial"
        elif " APT " in upper_line:
            classification = "Residential"
            
        # 2. Check Suspect List
        if classification == "Unknown" and addr_key in suspect_addresses:
            classification = "Review Required"
            
        # 3. Check Streets
        if classification == "Unknown":
            if street in CONFIRMED_RESIDENTIAL:
                classification = "Residential"
            elif street in REVIEW_STREETS:
                classification = "Residential" # Mixed street, not suspect -> Residential
            else:
                classification = "Residential" # Unknown -> Residential
        
        # 4. Override
        if street == 'PAXTON DR' or street == 'PAXTON DR S':
            classification = "Residential"

        # Filter
        if classification == "Residential":
            f_out.write(line + '\n')
            kept_count += 1
        else:
            removed_count += 1

print(f"Processing Complete.")
print(f"Kept: {kept_count}")
print(f"Removed: {removed_count}")
