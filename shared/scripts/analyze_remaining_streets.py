import csv
import re
from collections import Counter

input_file = 'addresses_43223_formatted.csv'

def get_street(address):
    parts = address.split(',')
    if len(parts) >= 1:
        street_part = parts[0].strip()
        # Remove leading numbers
        match = re.search(r'^\d+\s+(.*)', street_part)
        if match:
            return match.group(1).strip().upper()
        return street_part.strip().upper()
    return ""

street_counts = Counter()

with open(input_file, 'r') as f:
    reader = csv.reader(f)
    next(reader) # Skip header
    for row in reader:
        if row:
            street = get_street(row[0])
            street_counts[street] += 1

print("Top 50 Streets:")
for street, count in street_counts.most_common(50):
    print(f"{street}: {count}")

print(f"\nTotal Unique Streets: {len(street_counts)}")
