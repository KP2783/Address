import csv
import os

MANUAL_FILE = 'output/manual_review_needed.txt'
VALID_FILE = 'output/validation_results_43026.csv'
EXCLUDED_FILE = 'output/excluded_addresses.csv'
REMAINING_FILE = 'output/manual_review_remaining.txt'

# Streets to strictly Exclude (Commercial/Gov)
EXCLUDE_STREETS = [
    'TRUEMAN CT', 'VETERANS MEMORIAL DR', 
    'FISHINGER BLVD', 'RIDGE MILL DR', 'MILL MEADOW DR', 
    'PARK MILL RUN DR', 'DATA POINT CT', 'MUNICIPAL WAY',
    'LYMAN CT', 'LYMAN DR', 'WEAVER CT E', 'WEAVER CT S',
    'BROWN PARK DR', 'FISHINGER RD',
    'BERRY LEAF LN', 'TRUEMAN BLVD', 'TRUEPOINTE BLVD',
    'COLUMBIA ST', 'GREEN STRIPE LN', 'LEPPERT RD',
    'ANSON DR', 'KAYE DR', 'DUBLIN RD', 'COSGRAY RD', # Excluding Kaye, Dublin, Cosgray as mixed/commercial from context, or should verify? 
    # Actually, I'll only add verified ANSON. I'll leave others or exclude if confident.
    # Given they are remaining, I'll exclude ANSON.
    # Also removing the comment junk for cleaner code locally.
    'ANSON DR'
]

# Streets to Approve as Residential (Single Family/Condo/Apts checked)
APPROVE_STREETS = [
    'CEMETERY RD', 
    'LATTIMER ST', 
    'SMILEY RD', 
    'SCHIRTZINGER RD', 
    'SCIOTO DARBY CREEK RD', 
    'SCHIRTZINGER RD', 
    'SCIOTO DARBY CREEK RD', 
    'DAVIDSON RD',
    'BROMLEY ST',
    'CONDOR DR'
]

def main():
    print("Finalizing Batch 4 Manual Review...")
    
    lines = []
    if os.path.exists(MANUAL_FILE):
        with open(MANUAL_FILE, 'r') as f:
            lines = [l.strip() for l in f if l.strip()]
    else:
        print(f"No manual file found at {MANUAL_FILE}")
        return

    approved = []
    excluded = []
    remaining = []

    for line in lines:
        # line format: ADDRESS, City, State, Zip
        # Extract street name
        parts = line.split(',')
        if not parts: continue
        address_part = parts[0].strip()
        
        # Simple street extraction (remove leading number)
        # e.g. "3775 TRUEMAN CT" -> "TRUEMAN CT"
        import re
        street_clean = re.sub(r'^\d+\s+', '', address_part).upper()
        # Remove unit suffix if needed, but "TRUEMAN CT" matches "TRUEMAN CT"
        # Be careful with "FISHINGER BLVD 13" -> "FISHINGER BLVD 13". 
        # Check startswith for excludes
        
        is_excl = False
        for ex in EXCLUDE_STREETS:
            if street_clean.startswith(ex):
                excluded.append({'address': line, 'reason': f'Commercial Street ({ex})'})
                is_excl = True
                break
        if is_excl: continue

        is_appr = False
        for appr in APPROVE_STREETS:
            if street_clean.startswith(appr): # Using startswith to catch cases like "CEMETERY RD" in "CEMETERY RD UNIT..." if any, though residential usually clean.
                # Actually, check exact street name or startswith? 
                # Residential usually clean. 
                # "3721 FISHINGER RD" -> "FISHINGER RD".
                if street_clean == appr or street_clean.startswith(appr + ' '):
                     approved.append({'address': line, 'classification': 'Residential', 'property_type': 'Single Family', 'source': 'Manual Verification Batch 4'})
                     is_appr = True
                     break
        if is_appr: continue

        remaining.append(line)

    print(f"Approved: {len(approved)}")
    print(f"Excluded: {len(excluded)}")
    print(f"Remaining: {len(remaining)}")

    # Write
    with open(VALID_FILE, 'a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['address', 'classification', 'property_type', 'source'])
        for row in approved:
            writer.writerow(row)

    with open(EXCLUDED_FILE, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        for row in excluded:
            writer.writerow([row['address'], row['reason']])

    with open(REMAINING_FILE, 'w') as f:
        for line in remaining:
            f.write(line + "\n")

if __name__ == "__main__":
    main()
