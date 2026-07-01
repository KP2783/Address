import csv
import re
import os

# Commercial keywords in unit field
COMMERCIAL_UNIT_KEYWORDS = {'STE', 'SUITE', 'FLOOR', 'FL', 'BLDG', 'LOBBY', 'OFFICE', 'OFC'}

# Known commercial/institutional street patterns
COMMERCIAL_STREETS = {
    'ROCKWELL DISTRICT LN',
    'ROCKWELL DISTRICT LN S',
}

# Known residential streets (high confidence)
RESIDENTIAL_STREETS = {
    'FOUNTAIN LN', 'MAYFAIR BLVD', 'PARKLAWN BLVD', 'EASTPOINTE RIDGE DR',
    'RICKENBACKER AVE', 'S NAPOLEON AVE', 'FAIRWAY BLVD', 'STONE RIDGE DR',
    'IRONGATE LN', 'S ASHBURTON RD', 'BARNETT RD', 'GREAT OAK DR',
    'S WEYANT AVE', 'S YEARLING RD', 'MAPLEWOOD AVE', 'BEVERLY HILLS DR',
    'ROBINWOOD AVE', 'S HAMPTON RD', 'DONEY ST', 'EASTWAY CT',
    'COLLINGWOOD AVE', 'BEECHBANK RD', 'S JAMES RD', 'STONE RIDGE RD S',
    'GATEHOUSE DR', 'BEECHCREEK RD', 'WESTPHAL AVE', 'GREAT OAK WAY',
    'LONGBRANCH LN', 'RIVER RIDGE RD', 'PARLIAMENT DR', 'WOODCLIFF DR',
    'MARKHAM GREEN WAY', 'BROADMOOR AVE', 'N HAMPTON RD', 'BEECHTREE RD',
}

# Mixed streets (commercial corridor but has apartments)
MIXED_STREETS = {
    'E BROAD ST', 'E MAIN ST', 'HAMILTON RD', 'S HAMILTON RD',
}


def normalize_street(street):
    """Normalize extra whitespace in street names."""
    return re.sub(r'\s+', ' ', street).strip().upper()


def is_commercial_unit(unit):
    """Check if unit field indicates a commercial address."""
    if not unit:
        return False
    u = unit.upper().strip()
    for kw in COMMERCIAL_UNIT_KEYWORDS:
        if kw in u:
            return True
    return False


def classify(row):
    """Returns 'residential', 'commercial', or 'unknown'."""
    street = normalize_street(row['street'])
    unit = row.get('unit', '')
    number = row.get('number', '')

    # 1. Commercial unit keywords -> commercial
    if is_commercial_unit(unit):
        return 'commercial', 'commercial unit keyword'

    # 2. Known commercial streets -> commercial
    if street in COMMERCIAL_STREETS:
        return 'commercial', 'commercial street'

    # 3. Known residential streets -> residential
    if street in RESIDENTIAL_STREETS:
        return 'residential', 'known residential street'

    # 4. Mixed streets - keep apartments, remove bare commercial-looking addresses
    if street in MIXED_STREETS:
        if unit:
            u = unit.upper()
            if 'APT' in u or 'UNIT' in u or u.isdigit() or re.match(r'^[A-H]$', u):
                return 'residential', 'mixed street with residential unit'
        # Bare address on mixed street - still keep (could be house)
        return 'residential', 'mixed street bare address'

    # 5. Default: residential
    return 'residential', 'default residential'


def main():
    input_file = '/Users/kevinpatel/Address/43213_project/data/addresses_43213.csv'
    output_csv = '/Users/kevinpatel/Address/43213_project/data/addresses_43213_residential.csv'
    output_fmt = '/Users/kevinpatel/Address/43213_project/data/addresses_43213_formatted.csv'

    kept = []
    removed = []

    with open(input_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            classification, reason = classify(row)
            if classification == 'residential':
                kept.append(row)
            else:
                removed.append((row, reason))

    # Write residential CSV
    fieldnames = ['number', 'street', 'unit', 'city', 'region', 'postcode', 'district', 'latitude', 'longitude']
    with open(output_csv, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(kept)

    # Write formatted CSV (overwrite)
    with open(output_fmt, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['address'])
        for row in kept:
            street = normalize_street(row['street'])
            unit_part = f" {row['unit']}" if row['unit'] else ''
            city = row['city'] if row['city'] else 'Columbus'
            addr = f"{row['number']} {street}{unit_part}, {city}, OH, 43213"
            writer.writerow([addr])

    print(f"Total addresses: {len(kept) + len(removed)}")
    print(f"Kept (residential): {len(kept)}")
    print(f"Removed (commercial): {len(removed)}")
    print(f"\nRemoved breakdown:")
    reasons = {}
    for row, reason in removed:
        reasons[reason] = reasons.get(reason, 0) + 1
    for reason, count in sorted(reasons.items(), key=lambda x: -x[1]):
        print(f"  {reason}: {count}")

    print(f"\nSample removed addresses:")
    for row, reason in removed[:20]:
        street = normalize_street(row['street'])
        print(f"  {row['number']} {street} {row['unit']} - {reason}")


if __name__ == '__main__':
    main()
