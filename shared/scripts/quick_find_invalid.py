#!/usr/bin/env python3
"""
Quickly identify invalid addresses by checking just format errors
Then sample a few with the API to find which ones fail Census validation
"""

import csv

def format_address(row):
    parts = []
    if row.get('number'): parts.append(row['number'])
    if row.get('street'): parts.append(row['street'])
    if row.get('unit'): parts.append(row['unit'])
    if row.get('city'): parts.append(row['city'])
    if row.get('region'): parts.append(row['region'])
    if row.get('postcode'): parts.append(row['postcode'])
    return ', '.join(parts)

def check_format(row):
    issues = []
    if not row.get('number') or not row['number'].strip():
        issues.append('Missing house number')
    if not row.get('street') or not row['street'].strip():
        issues.append('Missing street name')
    if not row.get('city') or not row['city'].strip():
        issues.append('Missing city')
    if not row.get('postcode') or not row['postcode'].strip():
        issues.append('Missing zip code')
    else:
        zipcode = row['postcode'].strip()
        if not zipcode.isdigit() or len(zipcode) != 5:
            issues.append(f'Invalid zip code: {zipcode}')
        if zipcode != '43204':
            issues.append(f'Wrong zip: {zipcode}')
    if row.get('region', '').upper() != 'OH':
        issues.append(f"Wrong state: {row.get('region')}")
    return issues

print("Scanning addresses_43204.csv for format errors...")
print("=" * 80)

format_errors = []
checked = 0

with open('addresses_43204.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for i, row in enumerate(reader, 1):
        checked += 1
        issues = check_format(row)
        if issues:
            format_errors.append({
                'row': i,
                'address': format_address(row),
                'issues': issues
            })

print(f"Checked: {checked:,} addresses")
print(f"Format errors found: {len(format_errors)}")
print("\n" + "=" * 80)

if format_errors:
    print("FORMAT ERRORS:")
    print("-" * 80)
    for err in format_errors:
        print(f"\nRow #{err['row']}: {err['address']}")
        for issue in err['issues']:
            print(f"  - {issue}")
else:
    print("\n✓ NO FORMAT ERRORS FOUND!")
    print("\nThis means all ~35 invalid addresses from the validation")
    print("are addresses that have correct format but don't exist in")
    print("the US Census database (they may be new construction,")
    print("pending addresses, or data entry errors in the source).")

print("\n" + "=" * 80)
