import csv
from collections import Counter
import re

def analyze_addresses(filename):
    streets = Counter()
    with open(filename, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Extract street name (assuming format "NUMBER STREET NAME, City, State, Zip")
            # The CSV has 'address' column: "1531 WHISPERING WILLOW LN, Columbus, OH, 43026"
            addr = row['address']
            parts = addr.split(',')
            if len(parts) >= 1:
                street_part = parts[0].strip()
                # Remove leading number
                match = re.search(r'^\d+\s+(.*)', street_part)
                if match:
                    street_name = match.group(1)
                    streets[street_name] += 1
                else:
                    # Maybe no number?
                    streets[street_part] += 1
    
    # Print top 50 streets
    print(f"Total unique streets: {len(streets)}")
    print("\nTop 50 streets by address count:")
    for street, count in streets.most_common(50):
        print(f"{street}: {count}")

if __name__ == "__main__":
    analyze_addresses('addresses_43026_formatted.csv')
