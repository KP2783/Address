#!/usr/bin/env python3
"""
Add pattern-matched RESIDENTIAL classification for obvious apartment addresses.
APT and UNIT addresses are always residential - no API needed.
"""

import csv
import os

INPUT_FILE = '/Users/kevinpatel/Address/43026_project/data/addresses_43026_formatted.csv'
OUTPUT_FILE = '/Users/kevinpatel/Address/43026_project/output/smarty_validation_results.csv'

def is_apartment(address: str) -> bool:
    """Check if address is an apartment/unit - always residential."""
    addr_upper = address.upper()
    return ' APT ' in addr_upper or ' UNIT ' in addr_upper

def main():
    # Load already processed addresses (API results)
    already_processed = set()
    if os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                already_processed.add(row['address'])
        print(f"Already processed (API): {len(already_processed)} addresses")

    # Find apartment addresses not yet processed
    apartments_to_add = []
    with open(INPUT_FILE, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            addr = row['address']
            if addr not in already_processed and is_apartment(addr):
                apartments_to_add.append(addr)

    print(f"Apartment addresses to add: {len(apartments_to_add)}")

    # Append apartment addresses as RESIDENTIAL
    if apartments_to_add:
        with open(OUTPUT_FILE, 'a', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['address', 'classification', 'rdi', 'dpv_match', 'source'])
            for addr in apartments_to_add:
                writer.writerow({
                    'address': addr,
                    'classification': 'RESIDENTIAL',
                    'rdi': 'Residential',
                    'dpv_match': 'auto',
                    'source': 'pattern_apt'
                })
        print(f"Added {len(apartments_to_add)} apartment addresses")

    # Final count
    total = 0
    counts = {}
    source_counts = {}
    with open(OUTPUT_FILE, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            total += 1
            c = row['classification']
            s = row.get('source', 'unknown')
            counts[c] = counts.get(c, 0) + 1
            source_counts[s] = source_counts.get(s, 0) + 1

    print(f"\n=== Summary ===")
    print(f"Total processed: {total}")
    print(f"Remaining: {27057 - total}")
    print(f"\nBy classification:")
    for k, v in sorted(counts.items()):
        print(f"  {k}: {v} ({v/total*100:.1f}%)")
    print(f"\nBy source:")
    for k, v in sorted(source_counts.items()):
        print(f"  {k}: {v}")

if __name__ == "__main__":
    main()
