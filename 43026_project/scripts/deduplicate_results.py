import csv
import shutil
import os

VALIDATION_FILE = 'output/validation_results_43026.csv'
EXCLUDED_FILE = 'output/excluded_addresses.csv'

def deduplicate_file(filepath):
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return

    print(f"Processing {filepath}...")
    
    # Read all rows
    with open(filepath, 'r', newline='') as f:
        reader = csv.reader(f)
        try:
            header = next(reader)
            # Check if header is actually a data row (Batch 1-13 files didn't have consistent headers)
            # If the first item looks like an address (starts with number), it's data
            has_header = False
            if header and not header[0].strip()[0].isdigit():
                 has_header = True
            else:
                 # Reset file pointer if no header
                 f.seek(0)
                 header = []
            
            rows = list(reader) if has_header else [header] + list(reader)
            
        except StopIteration:
            print("File is empty.")
            return

    original_count = len(rows)
    
    # Deduplicate based on the first column (Address) or full row consistency
    unique_rows = []
    seen_addresses = set()
    
    for row in rows:
        if not row: continue
        
        # Normalize address for key (uppercase, stripped)
        addr_key = row[0].upper().strip().strip('"').strip("'")
        
        if addr_key not in seen_addresses:
            unique_rows.append(row)
            seen_addresses.add(addr_key)
        else:
            # If we want to keep the "better" classification, we could checking here.
            # For now, keeping the first occurrence is standard unless we know later batches corrected earlier ones.
            # Given the flow, later appends might be better? 
            # Actually, standardizing on keeping the LAST verified status might be safer if corrections were made,
            # but usually duplicates are just re-runs. 
            # Let's clean duplicates by keeping the FIRST seen for simplicity, 
            # assuming conflicts are rare or handled by the exclusion list overriding valid file.
            pass

    unique_count = len(unique_rows)
    print(f"Original lines: {original_count}, Unique lines: {unique_count}, Removed: {original_count - unique_count}")

    # Backup
    shutil.copy(filepath, filepath + '.bak')
    
    # Write back
    with open(filepath, 'w', newline='') as f:
        writer = csv.writer(f)
        if has_header:
            writer.writerow(header)
        writer.writerows(unique_rows)

if __name__ == "__main__":
    deduplicate_file(VALIDATION_FILE)
    deduplicate_file(EXCLUDED_FILE)
