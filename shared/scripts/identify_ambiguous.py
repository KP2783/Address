import csv
import re

MIXED_STREETS = {
    'SULLIVANT AVE', 'W MOUND ST', 'HARRISBURG PIKE', 'W RICH ST', 
    'FRANK RD', 'HARMON AVE', 'EAKIN RD', 'W BROAD ST'
}

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
ambiguous_addresses = []

with open(input_file, 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        addr = row['address']
        upper_addr = addr.upper()
        street = get_street(addr)
        
        if street in MIXED_STREETS:
            # Check if it has residential markers
            if " APT " in upper_addr or " UNIT " in upper_addr or " REAR " in upper_addr or " 1/2 " in upper_addr:
                continue
            
            # Check if it has commercial markers (already removed, but just in case)
            if " SUITE " in upper_addr or " STE " in upper_addr:
                continue
                
            # These are the ambiguous ones: "123 Sullivant Ave"
            ambiguous_addresses.append(addr)

print(f"Found {len(ambiguous_addresses)} ambiguous addresses on mixed streets.")
# Print sample
for a in ambiguous_addresses[:20]:
    print(a)
