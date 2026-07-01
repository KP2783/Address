import csv
import re

MIXED_STREETS = {
    'SULLIVANT AVE', 'W MOUND ST', 'HARRISBURG PIKE', 'W RICH ST', 
    'FRANK RD', 'HARMON AVE', 'EAKIN RD', 'W BROAD ST'
}

input_file = 'addresses_43223_formatted.csv'

mixed_street_addresses = []
unit_addresses = []
potential_commercial_keywords = []

keywords = ['INC', 'LLC', 'CO', 'COMPANY', 'CORP', 'CENTER', 'PLAZA', 'SHOP', 'STORE', 'MARKET', 'BANK', 'SCHOOL', 'CHURCH']

with open(input_file, 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        addr = row['address']
        upper_addr = addr.upper()
        
        # Check Mixed Streets
        is_mixed = False
        for street in MIXED_STREETS:
            if street in upper_addr:
                mixed_street_addresses.append(addr)
                is_mixed = True
                break
        
        # Check Units
        if " UNIT " in upper_addr or " APT " in upper_addr or " # " in upper_addr:
            unit_addresses.append(addr)
            
        # Check Keywords
        for kw in keywords:
            # Check for whole word match
            if re.search(r'\b' + kw + r'\b', upper_addr):
                potential_commercial_keywords.append(addr)
                break

print(f"Total Remaining: {sum(1 for _ in open(input_file)) - 1}")
print(f"Addresses on Mixed Streets: {len(mixed_street_addresses)}")
print(f"Addresses with Units: {len(unit_addresses)}")
print(f"Addresses with Commercial Keywords: {len(potential_commercial_keywords)}")

print("\n--- Sample Mixed Street Addresses ---")
for a in mixed_street_addresses[:20]:
    print(a)

print("\n--- Sample Commercial Keywords ---")
for a in potential_commercial_keywords[:20]:
    print(a)
