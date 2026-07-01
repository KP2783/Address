#!/usr/bin/env python3
"""
Re-run validation on just the first 7000 addresses and SAVE invalid ones to a file
This runs in parallel with the main validation to give us the list NOW
"""

import csv
import json
import urllib.request
import urllib.parse
import time

census_api_url = "https://geocoding.geo.census.gov/geocoder/locations/onelineaddress"

def format_address(row):
    parts = []
    if row.get('number'): parts.append(row['number'])
    if row.get('street'): parts.append(row['street'])
    if row.get('unit'): parts.append(row['unit'])
    if row.get('city'): parts.append(row['city'])
    if row.get('region'): parts.append(row['region'])
    if row.get('postcode'): parts.append(row['postcode'])
    return ', '.join(parts)

def validate_with_api(address):
    try:
        params = {
            'address': address,
            'benchmark': 'Public_AR_Current',
            'format': 'json'
        }
        url = f"{census_api_url}?{urllib.parse.urlencode(params)}"
        with urllib.request.urlopen(url, timeout=10) as response:
            data = json.loads(response.read().decode())
            if 'result' in data and 'addressMatches' in data['result']:
                matches = data['result']['addressMatches']
                return len(matches) > 0
    except:
        pass
    return False

print("=" * 80)
print("EXTRACTING INVALID ADDRESSES (first 7000)")
print("=" * 80)
print("This will identify which specific addresses failed validation...")
print()

invalid_list = []
checked = 0

with open('addresses_43204.csv', 'r') as f:
    reader = csv.DictReader(f)
    for i, row in enumerate(reader, 1):
        if i > 7000:
            break

        checked += 1
        address = format_address(row)

        if not validate_with_api(address):
            invalid_list.append({
                'row_number': i,
                'address': address,
                'original_data': row
            })
            print(f"✗ Row {i:5d}: {address}")

        if i % 100 == 0:
            print(f"  Checked {i}... (found {len(invalid_list)} invalid)", end='\r')

        time.sleep(0.2)  # Rate limiting

print("\n\n" + "=" * 80)
print(f"RESULTS: Found {len(invalid_list)} invalid addresses out of {checked}")
print("=" * 80)

# Save to file
with open('invalid_addresses_detailed.json', 'w') as f:
    json.dump(invalid_list, f, indent=2)

print("\n\nINVALID ADDRESSES:")
print("-" * 80)
for item in invalid_list:
    print(f"\nRow #{item['row_number']}: {item['address']}")

print(f"\n\nSaved to: invalid_addresses_detailed.json")
