#!/usr/bin/env python3
"""
Create clean CSV with only VALID addresses
Uses the Census-matched addresses WITHOUT quotes
"""

import csv

print("Creating clean CSV with valid addresses only (no quotes)...")

valid_count = 0
input_file = 'validation_results_detailed.csv'
output_file = 'addresses_43204_valid_clean.csv'

with open(input_file, 'r', encoding='utf-8') as infile:
    with open(output_file, 'w', newline='', encoding='utf-8') as outfile:
        reader = csv.DictReader(infile)
        
        # Write header
        outfile.write('address,latitude,longitude\n')
        
        for row in reader:
            # Only process VALID addresses
            if row['validation_status'] == 'VALID':
                # Use the matched_address from Census (already standardized)
                matched_addr = row['matched_address']
                lat = row['latitude']
                lon = row['longitude']
                
                # Write without quotes - write directly as string
                outfile.write(f'{matched_addr},{lat},{lon}\n')
                valid_count += 1

print(f"\n✓ Created {output_file}")
print(f"✓ Total valid addresses: {valid_count:,}")
print(f"\nFile format:")
print("  - Column 1: Clean address (Census standardized, no quotes)")
print("  - Column 2: Latitude")
print("  - Column 3: Longitude")
