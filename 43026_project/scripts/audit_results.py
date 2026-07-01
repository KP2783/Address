import csv

VALIDATION_FILE = 'output/validation_results_43026.csv'
EXCLUDED_FILE = 'output/excluded_addresses.csv'

def audit_files():
    print("Auditing Output Files...")
    
    verified = {}
    verified_duplicates = 0
    with open(VALIDATION_FILE, 'r') as f:
        reader = csv.reader(f)
        try:
            header = next(reader) # skip header implied or check it
        except StopIteration:
            pass
            
        for row in reader:
            if not row: continue
            addr = row[0].upper().strip().strip('"').strip("'")
            if addr in verified:
                verified_duplicates += 1
            else:
                verified[addr] = row

    excluded = {}
    excluded_duplicates = 0
    with open(EXCLUDED_FILE, 'r') as f:
        reader = csv.reader(f)
        try:
            header = next(reader)
        except StopIteration:
            pass

        for row in reader:
            if not row: continue
            addr = row[0].upper().strip().strip('"').strip("'")
            if addr in excluded:
                excluded_duplicates += 1
            else:
                excluded[addr] = row

    print(f"Verified Unique: {len(verified)}")
    print(f"Verified Duplicates Found: {verified_duplicates}")
    print(f"Excluded Unique: {len(excluded)}")
    print(f"Excluded Duplicates Found: {excluded_duplicates}")

    # Check Overlaps
    overlaps = []
    for addr in verified:
        if addr in excluded:
            overlaps.append(addr)
    
    print(f"Overlap Count (In Both Files): {len(overlaps)}")
    if overlaps:
        print("Sample Overlaps:")
        for addr in overlaps[:10]:
            print(f" - {addr}")
            print(f"   Verified Row: {verified[addr]}")
            print(f"   Excluded Row: {excluded[addr]}")

    # Check Format (Basic check for column count)
    # verified usually has 4 cols: Address, Class, Type, Source
    # excluded usually has 2: Address, Reason
    bad_format_verified = 0
    for row in verified.values():
        if len(row) < 2:
            bad_format_verified += 1
            
    print(f"Bad Format Rows (Verified): {bad_format_verified}")

if __name__ == "__main__":
    audit_files()
