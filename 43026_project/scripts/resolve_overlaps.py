import csv
import os
import shutil

VALIDATION_FILE = 'output/validation_results_43026.csv'
EXCLUDED_FILE = 'output/excluded_addresses.csv'

def resolve_conflicts():
    print("Resolving Conflicts (Excluded takes precedence)...")
    
    # Load Excluded Addresses
    excluded_set = set()
    with open(EXCLUDED_FILE, 'r') as f:
        reader = csv.reader(f)
        try:
            next(reader) # skip header
        except StopIteration:
            pass
        for row in reader:
            if row:
                excluded_set.add(row[0].upper().strip().strip('"').strip("'"))
    
    print(f"Loaded {len(excluded_set)} excluded addresses.")

    # Filter Validation File
    cleaned_rows = []
    removed_count = 0
    
    with open(VALIDATION_FILE, 'r') as f:
        reader = csv.reader(f)
        try:
            header = next(reader)
        except StopIteration:
            header = []
            
        for row in reader:
            if not row: continue
            addr = row[0].upper().strip().strip('"').strip("'")
            
            if addr in excluded_set:
                removed_count += 1
                # print(f"Removing conflict: {addr}")
            else:
                cleaned_rows.append(row)

    print(f"Removed {removed_count} conflicting addresses from verified list.")
    
    # Write back
    shutil.copy(VALIDATION_FILE, VALIDATION_FILE + '.audit_bak')
    
    with open(VALIDATION_FILE, 'w', newline='') as f:
        writer = csv.writer(f)
        if header:
            writer.writerow(header)
        writer.writerows(cleaned_rows)

if __name__ == "__main__":
    resolve_conflicts()
