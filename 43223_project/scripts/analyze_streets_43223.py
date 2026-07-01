import csv
from collections import Counter
import re

def analyze_streets(filename):
    streets = Counter()
    with open(filename, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            addr = row['address']
            # Format: "123 Street Name, City, OH 43223"
            parts = addr.split(',')
            if len(parts) >= 1:
                street_part = parts[0].strip()
                match = re.search(r'^\d+\s+(.*)', street_part)
                if match:
                    street_name = match.group(1).strip().upper()
                    streets[street_name] += 1
                else:
                    streets[street_part.strip().upper()] += 1
    
    print(f"Total unique streets: {len(streets)}")
    print("\nTop 50 streets by address count:")
    for street, count in streets.most_common(50):
        print(f"{street}: {count}")

if __name__ == "__main__":
    analyze_streets('addresses_43223_formatted.csv')
