import csv
import os

SOURCE_FILE = 'data/addresses_43026.csv'
VALIDATION_FILE = 'output/validation_results_43026.csv'
EXCLUDED_FILE = 'output/excluded_addresses.csv'
MANUAL_FILE = 'output/manual_review_remaining.txt'

def normalize(addr):
    if not addr: return ""
    return addr.upper().strip().strip('"').strip("'")

def detailed_audit():
    print("Starting Detailed Audit...")

    # 1. Load Source (Structured CSV: number,street,unit,city,region,postcode...)
    source_set = set()
    with open(SOURCE_FILE, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Construct address: "NUMBER STREET UNIT, CITY, STATE, POSTCODE"
            # Handling unit if present
            unit = row.get('unit', '').strip()
            street = row.get('street', '').strip()
            number = row.get('number', '').strip()
            
            # Basic construction to match output format roughly
            # Output format saw: "1531 WHISPERING WILLOW LN, Columbus, OH, 43026"
            # Source: 3983,MAIN ST,,Hilliard,OH,43026
            
            full_addr = f"{number} {street}"
            if unit:
                full_addr += f" {unit}"
            
            full_addr += f", {row.get('city','')}, {row.get('region','')}, {row.get('postcode','')}"
            
            source_set.add(normalize(full_addr))
    
    print(f"Source Total Unique Addresses: {len(source_set)}")

    # 2. Analyze Validation File
    verified_set = set()
    unknown_status_count = 0
    unknown_rows = []
    
    with open(VALIDATION_FILE, 'r') as f:
        reader = csv.reader(f)
        header = next(reader, [])
        for row in reader:
            if not row: continue
            addr = normalize(row[0])
            verified_set.add(addr)
            
            # Check for "Unknown" in columns
            row_str = str(row).upper()
            if "UNKNOWN" in row_str or "MANUAL" in row_str or "REVIEW" in row_str:
                unknown_status_count += 1
                unknown_rows.append(row)

    print(f"Verified Residential Unique: {len(verified_set)}")
    print(f"Rows with 'Unknown' or 'Manual' status in Verified File: {unknown_status_count}")
    if unknown_rows:
        print("Sample 'Unknown' Verified Columns:")
        for r in unknown_rows[:5]:
            print(f" - {r}")

    # 3. Analyze Excluded File
    excluded_set = set()
    with open(EXCLUDED_FILE, 'r') as f:
        reader = csv.reader(f)
        next(reader, []) # Skip header
        for row in reader:
            if row:
                excluded_set.add(normalize(row[0]))

    print(f"Excluded Unique: {len(excluded_set)}")

    # 4. Analyze Manual Review Pending
    manual_set = set()
    if os.path.exists(MANUAL_FILE):
        with open(MANUAL_FILE, 'r') as f:
            for line in f:
                if line.strip():
                    manual_set.add(normalize(line.strip()))
    
    print(f"Manual Review Pending (Text File): {len(manual_set)}")

    # 5. Calculate Overlaps & Remaining
    # Processed = Verified OR Excluded
    processed_set = verified_set.union(excluded_set)
    
    # Check intersection with Source
    # Note: Source might have slight formatting diffs vs output if output was normalized.
    # But usually we kept the original string.
    
    # Let's check how many Source items are in Processed
    completed_from_source = 0
    remaining_list = []
    
    for src_addr in source_set:
        if src_addr in processed_set:
            completed_from_source += 1
        else:
            remaining_list.append(src_addr)

    print("-" * 30)
    print(f"Source Addresses Processed: {completed_from_source}")
    print(f"Source Addresses Remaining: {len(remaining_list)}")
    print("-" * 30)
    
    # 6. Check what IS in remaining_list - is it mostly new stuff or stuff we missed?
    print("Sample Remaining Addresses:")
    for addr in remaining_list[:10]:
        print(f" - {addr}")

if __name__ == "__main__":
    detailed_audit()
