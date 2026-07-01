import csv
import re

# Load confirmed residential streets (I'll add the ones I found)
CONFIRMED_RESIDENTIAL = {
    'SINGLETON DR', 'STONEYBROOK BLVD', 'BLUEMONT PK', 'FISHINGER MILL DR', 
    'RIDGEBURY DR', 'RAVENNA LOOP', 'BENNIGAN DR', 'BRIDLE CREEK WAY', 
    'BLUEBIRD PL', 'SEDGE LN', 'BROOKLANDS DR', 'WOODLAND DR', 
    'MESSNER DR', 'RIDGEWOOD DR', 'PEPPER BERRY LN', 'BLUE LAGOON LN', 
    'VALENCIA PARK BLVD', 'WHISPERING WILLOW LN', 'BENDING WILLOW LN',
    'PAXTON DR' # Confirmed residential
}

# Load review streets
REVIEW_STREETS = {
    'AVERY RD', 'BALDWIN RD', 'CAMERON RD', 'CEMETERY RD', 'CENTER ST', 
    'COSGRAY RD', 'DAVIDSON RD', 'DAVIS RD', 'DUBLIN RD', 'ELLIOTT RD', 
    'HAYDEN RUN RD', 'HIGH SCHOOL DR', 'JONES RD', 'KROEHLER DR', 
    'LEPPERT RD', 'MAIN ST', 'MORRIS RD', 'MUNICIPAL WAY', 'NORWICH ST', 
    'PATTERSON RD', 'PAXTON DR', 'ROBERTS RD', 'SCHIRTZINGER RD', 
    'SCIOTO DARBY CREEK RD', 'SMILEY RD', 'SPINDLER RD', 'TAYLOR LANE AVE', 
    'TRUEMAN BLVD', 'VETERANS MEMORIAL DR', 'WALKER RD',
    'SCIOTO DARBY RD', 'NIKE DR', 'LEAP CT' # Added from my search
}

unknown_streets = set()
unknown_count = 0

with open('addresses_43026_formatted.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        addr = row['address']
        parts = addr.split(',')
        if len(parts) >= 1:
            street_part = parts[0].strip()
            match = re.search(r'^\d+\s+(.*)', street_part)
            if match:
                street = match.group(1)
            else:
                street = street_part
            
            if street not in CONFIRMED_RESIDENTIAL and street not in REVIEW_STREETS:
                unknown_streets.add(street)
                unknown_count += 1

print(f"Unknown streets: {len(unknown_streets)}")
print(f"Addresses on unknown streets: {unknown_count}")
print("\nTop 20 Unknown Streets:")
# I need to count them to sort
from collections import Counter
street_counts = Counter()
with open('addresses_43026_formatted.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        addr = row['address']
        parts = addr.split(',')
        if len(parts) >= 1:
            street_part = parts[0].strip()
            match = re.search(r'^\d+\s+(.*)', street_part)
            if match:
                street = match.group(1)
            else:
                street = street_part
            
            if street not in CONFIRMED_RESIDENTIAL and street not in REVIEW_STREETS:
                street_counts[street] += 1

for s, c in street_counts.most_common(20):
    print(f"{s}: {c}")
