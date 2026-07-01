#!/usr/bin/env python3
"""
Convert addresses_all_zips_residential.txt to CSV format
"""
import csv
import re

def parse_address_line(line):
    """Parse a city, state, zip line into components"""
    # Format: City, State ZIP
    match = re.match(r'^(.+),\s+([A-Z]{2})\s+(\d{5})$', line.strip())
    if match:
        return match.group(1), match.group(2), match.group(3)
    return None, None, None

def convert_to_csv(input_file, output_file):
    """Convert text addresses to CSV format"""
    addresses = []

    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    i = 0
    while i < len(lines):
        line = lines[i].strip()

        # Skip empty lines and headers
        if not line or line.startswith('=') or 'ZIP CODE' in line or 'RESIDENTIAL MAILING' in line or 'Zip Codes:' in line or 'Total:' in line or 'Business addresses' in line:
            i += 1
            continue

        # Check if this is the start of an address entry (recipient name)
        if line == 'Current Resident' or (i + 2 < len(lines) and ',' in lines[i + 2]):
            recipient = line

            # Get the next two lines (street address and city/state/zip)
            if i + 2 < len(lines):
                street = lines[i + 1].strip()
                city_state_zip = lines[i + 2].strip()

                # Parse city, state, zip
                city, state, zip_code = parse_address_line(city_state_zip)

                if city and state and zip_code:
                    addresses.append({
                        'Recipient': recipient,
                        'Street Address': street,
                        'City': city,
                        'State': state,
                        'ZIP Code': zip_code
                    })

                i += 3  # Skip to next entry
            else:
                i += 1
        else:
            i += 1

    # Write to CSV
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['Recipient', 'Street Address', 'City', 'State', 'ZIP Code']
        writer = csv.DictWriter(f, fieldnames=fieldnames)

        writer.writeheader()
        writer.writerows(addresses)

    return len(addresses)

if __name__ == '__main__':
    input_file = 'addresses_all_zips_residential.txt'
    output_file = 'addresses_all_zips_residential.csv'

    print(f"Converting {input_file} to CSV format...")
    count = convert_to_csv(input_file, output_file)
    print(f"Successfully converted {count:,} addresses to {output_file}")
