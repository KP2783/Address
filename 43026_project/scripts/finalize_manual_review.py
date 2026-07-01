
import csv
import os

VALID_FILE = 'output/validation_results_43026.csv'
EXCLUDED_FILE = 'output/excluded_addresses.csv'
UNKNOWN_FILE = 'output/final_unknowns.txt'

# Data from Manual Verification
residential_adds = [
    {'address': '3200 CEMETERY RD, Hilliard, OH, 43026', 'classification': 'Residential', 'property_type': 'Single Family', 'source': 'Manual Verification'},
    {'address': '3334 CEMETERY RD, Hilliard, OH, 43026', 'classification': 'Residential', 'property_type': 'Single Family', 'source': 'Manual Verification'},
    {'address': '3377 CEMETERY RD, Hilliard, OH, 43026', 'classification': 'Residential', 'property_type': 'Single Family', 'source': 'Manual Verification'},
    {'address': '3383 SCHIRTZINGER RD, Hilliard, OH, 43026', 'classification': 'Residential', 'property_type': 'Single Family', 'source': 'Manual Verification'},
    {'address': '3390 SMILEY RD, Columbus, OH, 43026', 'classification': 'Residential', 'property_type': 'Single Family', 'source': 'Manual Verification'},
    {'address': '3450 CEMETERY RD, Hilliard, OH, 43026', 'classification': 'Residential', 'property_type': 'Single Family', 'source': 'Manual Verification'},
    {'address': '3455 SMILEY RD, Columbus, OH, 43026', 'classification': 'Residential', 'property_type': 'Single Family', 'source': 'Manual Verification'},
    {'address': '3470 SMILEY RD, Hilliard, OH, 43026', 'classification': 'Residential', 'property_type': 'Single Family', 'source': 'Manual Verification'},
    {'address': '3480 CEMETERY RD, Hilliard, OH, 43026', 'classification': 'Residential', 'property_type': 'Single Family', 'source': 'Manual Verification'},
    {'address': '3480 SMILEY RD, Hilliard, OH, 43026', 'classification': 'Residential', 'property_type': 'Single Family', 'source': 'Manual Verification'},
    {'address': '3495 CEMETERY RD, Hilliard, OH, 43026', 'classification': 'Residential', 'property_type': 'Single Family', 'source': 'Manual Verification'},
    {'address': '3500 CEMETERY RD, Hilliard, OH, 43026', 'classification': 'Residential', 'property_type': 'Single Family', 'source': 'Manual Verification'},
    {'address': '3500 SMILEY RD, Columbus, OH, 43026', 'classification': 'Residential', 'property_type': 'Single Family', 'source': 'Manual Verification'},
]

excluded_adds = [
    {'address': '3311 MILL MEADOW DR, Hilliard, OH, 43026', 'reason': 'Commercial (Flex/Light Dist)'},
    {'address': '3315 MILL MEADOW DR, Hilliard, OH, 43026', 'reason': 'Commercial (Flex/Light Dist)'},
    {'address': '3333 MILL MEADOW DR, Hilliard, OH, 43026', 'reason': 'Commercial (Tennis Club)'},
    {'address': '3436 HERITAGE CLUB DR, Hilliard, OH, 43026', 'reason': 'Commercial (Retail)'},
    {'address': '3438 HERITAGE CLUB DR, Hilliard, OH, 43026', 'reason': 'Commercial (Retail)'},
    {'address': '3440 HERITAGE CLUB DR, Hilliard, OH, 43026', 'reason': 'Commercial (Retail)'},
]

unknown_adds = [
    '2611 KINGVIEW DR, Hilliard, OH, 43026'
]

def main():
    # Append Valid
    with open(VALID_FILE, 'a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['address', 'classification', 'property_type', 'source'])
        for row in residential_adds:
            writer.writerow(row)
    print(f"Added {len(residential_adds)} residential addresses.")

    # Append Excluded
    with open(EXCLUDED_FILE, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        for row in excluded_adds:
            writer.writerow([row['address'], row['reason']])
    print(f"Added {len(excluded_adds)} excluded addresses.")

    # Save Unknowns
    with open(UNKNOWN_FILE, 'w') as f:
        for addr in unknown_adds:
            f.write(addr + "\n")
    print(f"Saved {len(unknown_adds)} unknown addresses to {UNKNOWN_FILE}")

if __name__ == "__main__":
    main()
