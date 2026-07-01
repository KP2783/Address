#!/usr/bin/env python3
"""
Rebuild split files from original data, keeping only RESIDENTIAL addresses.
Preserves full address format (with city, state, zip).
"""

import csv
import os
from glob import glob

# Paths
SMARTY_FILE = '/Users/kevinpatel/Address/43026_project/output/smarty_validation_results.csv'
ORIGINAL_FILE = '/Users/kevinpatel/Address/43026_project/data/addresses_43026_formatted.csv'
SPLIT_DIR = '/Users/kevinpatel/Address/43026_project/split_addresses_43026'

def extract_street(full_address):
    """Extract street portion from full address for matching."""
    # "1531 WHISPERING WILLOW LN, Columbus, OH, 43026" -> "1531 WHISPERING WILLOW LN"
    return full_address.split(',')[0].strip()

def main():
    # Load residential streets from Smarty results (street only, no city/state/zip)
    print("Loading Smarty validation results...")
    residential_streets = set()

    with open(SMARTY_FILE, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['classification'] == 'RESIDENTIAL':
                residential_streets.add(row['address'])

    print(f"RESIDENTIAL streets: {len(residential_streets)}")

    # Load original addresses with full format
    print("Loading original addresses...")
    original_addresses = []
    street_to_full = {}

    with open(ORIGINAL_FILE, 'r') as f:
        next(f)  # skip header
        for line in f:
            full_addr = line.strip()
            street = extract_street(full_addr)
            original_addresses.append(full_addr)
            street_to_full[street] = full_addr

    print(f"Total original addresses: {len(original_addresses)}")

    # Filter to residential only (preserving full format)
    residential_full = []
    for full_addr in original_addresses:
        street = extract_street(full_addr)
        if street in residential_streets:
            residential_full.append(full_addr)

    print(f"Residential with full format: {len(residential_full)}")

    # Split into files of ~1000 each
    chunk_size = 1000
    file_num = 1

    # Remove old split files first
    for old_file in glob(os.path.join(SPLIT_DIR, 'addresses_43026_part_*.csv')):
        os.remove(old_file)

    for i in range(0, len(residential_full), chunk_size):
        chunk = residential_full[i:i+chunk_size]
        filename = os.path.join(SPLIT_DIR, f'addresses_43026_part_{file_num:02d}.csv')

        with open(filename, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['address'])
            writer.writeheader()
            for addr in chunk:
                writer.writerow({'address': addr})

        print(f"  {os.path.basename(filename)}: {len(chunk)} addresses")
        file_num += 1

    print(f"\n=== Summary ===")
    print(f"Created {file_num - 1} split files")
    print(f"Total RESIDENTIAL addresses: {len(residential_full)}")

if __name__ == "__main__":
    main()
