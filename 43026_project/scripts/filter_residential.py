#!/usr/bin/env python3
"""
Filter split address files to keep only RESIDENTIAL addresses.
Uses smarty_validation_results.csv as source of truth.
"""

import csv
import os
from glob import glob

# Paths
SMARTY_FILE = '/Users/kevinpatel/Address/43026_project/output/smarty_validation_results.csv'
SPLIT_DIR = '/Users/kevinpatel/Address/43026_project/split_addresses_43026'

def main():
    # Load residential addresses from Smarty results
    print("Loading Smarty validation results...")
    residential_addresses = set()
    total_smarty = 0

    with open(SMARTY_FILE, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            total_smarty += 1
            if row['classification'] == 'RESIDENTIAL':
                residential_addresses.add(row['address'])

    print(f"Total in Smarty file: {total_smarty}")
    print(f"RESIDENTIAL addresses: {len(residential_addresses)}")

    # Process each split file
    split_files = sorted(glob(os.path.join(SPLIT_DIR, 'addresses_43026_part_*.csv')))
    print(f"\nProcessing {len(split_files)} split files...")

    total_original = 0
    total_kept = 0
    total_removed = 0

    for split_file in split_files:
        filename = os.path.basename(split_file)

        # Read all addresses from split file
        addresses = []
        with open(split_file, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                addresses.append(row['address'])

        original_count = len(addresses)

        # Filter to keep only residential
        residential_only = [addr for addr in addresses if addr in residential_addresses]
        kept_count = len(residential_only)
        removed_count = original_count - kept_count

        # Write back filtered addresses
        with open(split_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['address'])
            writer.writeheader()
            for addr in residential_only:
                writer.writerow({'address': addr})

        print(f"  {filename}: {original_count} -> {kept_count} (removed {removed_count})")

        total_original += original_count
        total_kept += kept_count
        total_removed += removed_count

    print(f"\n=== Summary ===")
    print(f"Total original: {total_original}")
    print(f"Total kept (RESIDENTIAL): {total_kept}")
    print(f"Total removed (COMMERCIAL/UNKNOWN): {total_removed}")
    print(f"Removal rate: {total_removed/total_original*100:.1f}%")

if __name__ == "__main__":
    main()
