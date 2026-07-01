import csv
import re

input_file = 'addresses_43223_formatted.csv'
output_file = 'review_candidates_43223.txt'

# Known mixed use or commercial heavy streets
MIXED_STREETS = [
    'SULLIVANT AVE', 'W MOUND ST', 'HARRISBURG PIKE', 'W RICH ST', 
    'FRANK RD', 'HARMON AVE', 'EAKIN RD', 'W BROAD ST', 'BRIGGS RD'
]

# Keywords that strongly suggest commercial
COMMERCIAL_KEYWORDS = [
    'INC', 'LLC', 'CO', 'COMPANY', 'CORP', 'LIMITED',
    'CENTER', 'PLAZA', 'SHOP', 'STORE', 'MARKET', 'MART',
    'BANK', 'SCHOOL', 'CHURCH', 'TEMPLE', 'CHAPEL',
    'AUTO', 'TIRE', 'SERVICE', 'REPAIR', 'GARAGE',
    'SALON', 'BARBER', 'BEAUTY', 'NAIL',
    'PIZZA', 'GRILL', 'CAFE', 'DINER', 'RESTAURANT', 'BAR', 'PUB',
    'OFFICE', 'SUITE', 'STE', 'BLDG', 'BUILDING', 'FLOOR',
    'ASSOC', 'CLUB', 'LODGE', 'POST', 'VFW',
    'STORAGE', 'WAREHOUSE',
    'PARK', 'GARDEN', 'VILLAGE' # Sometimes commercial, sometimes residential
]

# False positive street names to ignore for specific keywords
FALSE_POSITIVE_STREETS = {
    'PARK': ['PARK AVE', 'PARK ST', 'PARK DR', 'PARK CT', 'PARK PL', 'PARK RD'],
    'VILLAGE': ['VILLAGE DR', 'VILLAGE CT', 'VILLAGE LN', 'VILLAGE WAY', 'VILLAGE RD']
}

# Specific street names to check (like the Briggs Center Dr one)
SUSPICIOUS_STREET_NAMES = ['BRIGGS CENTER DR', 'CONSUMER SQ', 'WESTBELT DR']

candidates = {
    'keywords': [],
    'suspicious_street_names': [],
    'mixed_streets': [],
    'units_on_mixed': []
}

with open(input_file, 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        addr = row['address']
        upper_addr = addr.upper()
        
        # Check Suspicious Street Names
        for ssn in SUSPICIOUS_STREET_NAMES:
            if ssn in upper_addr:
                candidates['suspicious_street_names'].append(addr)
                break
        
        # Check Commercial Keywords
        found_keyword = False
        for kw in COMMERCIAL_KEYWORDS:
            # Word boundary check
            if re.search(r'\b' + kw + r'\b', upper_addr):
                # Check for false positives
                is_false_positive = False
                if kw in FALSE_POSITIVE_STREETS:
                    for fp_street in FALSE_POSITIVE_STREETS[kw]:
                        if fp_street in upper_addr:
                            is_false_positive = True
                            break
                
                if not is_false_positive:
                    candidates['keywords'].append((addr, kw))
                    found_keyword = True
                    break
        if found_keyword:
            continue

        # Check Mixed Streets
        for street in MIXED_STREETS:
            if street in upper_addr:
                if " UNIT " in upper_addr or " APT " in upper_addr or " # " in upper_addr:
                    candidates['units_on_mixed'].append(addr)
                else:
                    candidates['mixed_streets'].append(addr)
                break

with open(output_file, 'w') as f:
    f.write("REVIEW CANDIDATES FOR 43223\n")
    f.write("===========================\n\n")
    
    f.write(f"--- Suspicious Street Names ({len(candidates['suspicious_street_names'])}) ---\n")
    for addr in candidates['suspicious_street_names']:
        f.write(f"{addr}\n")
    f.write("\n")
    
    f.write(f"--- Commercial Keywords ({len(candidates['keywords'])}) ---\n")
    for addr, kw in candidates['keywords']:
        f.write(f"{addr} [Match: {kw}]\n")
    f.write("\n")
    
    f.write(f"--- Mixed Streets (Non-Unit) ({len(candidates['mixed_streets'])}) ---\n")
    f.write("(Check if these are single family homes or businesses)\n")
    for addr in candidates['mixed_streets']:
        f.write(f"{addr}\n")
    f.write("\n")

    f.write(f"--- Mixed Streets (Units/Apts) ({len(candidates['units_on_mixed'])}) ---\n")
    f.write("(Likely apartments, but check for 'Suite' or commercial units)\n")
    for addr in candidates['units_on_mixed']:
        f.write(f"{addr}\n")
    f.write("\n")

print(f"Generated {output_file}")
