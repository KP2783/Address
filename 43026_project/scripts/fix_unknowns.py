import csv
import sys
import os
import re

# Add local directory to path to import process_mega_batch_results
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from process_mega_batch_results import STREET_MAP, EXPLICIT_EXCLUDES, EXCLUDED_STREET_NAMES

VALIDATION_FILE = 'output/validation_results_43026.csv'
TEMP_FILE = 'output/validation_results_fixed.csv'

def clean_street_name(address_line):
    parts = address_line.split(',')
    if len(parts) >= 1:
        address_part = parts[0].strip()
        street = re.sub(r'^\d+\s+', '', address_part).strip()
        street = re.sub(r'\s+(UNIT|APT|STE|#).*$', '', street, flags=re.IGNORECASE)
        # Also clean up city/state if they leaked in
        street = street.split(' Hilliard')[0].split(' Columbus')[0]
        return street.upper().strip()
    return ""

def classify_address(addr):
    street = clean_street_name(addr)
    
    # Check Excludes
    for excl in EXPLICIT_EXCLUDES:
        if excl in addr.upper():
            return None
            
    # Check Excluded Streets
    if any(street.startswith(excl) for excl in EXCLUDED_STREET_NAMES):
        return None

    # Look up
    info = STREET_MAP.get(street)
    if not info:
         # Fuzzy
         norm_street = street.replace("'", "").replace(".", "")
         for k, v in STREET_MAP.items():
             if k.replace("'", "").replace(".", "") == norm_street:
                 info = v
                 break
    
    if info:
        if info['class'] == 'Residential':
             return {'class': 'Residential', 'type': info['type']}
        elif info['class'] == 'Check_Specific':
             return {'class': 'Residential', 'type': info['type']}
    
    return None

def fix_unknowns():
    print("Fixing 'Unknown' status rows...")
    
    rows = []
    fixed_count = 0
    
    with open(VALIDATION_FILE, 'r') as f:
        reader = csv.reader(f)
        try:
            header = next(reader)
        except StopIteration:
            header = ["address", "classification", "property_type", "source"]
            
        rows.append(header)
        
        for row in reader:
            if not row: continue
            
            addr_str = row[0]
            status_col = row[1].upper() if len(row) > 1 else ""
            
            if "UNKNOWN" in status_col or "MANUAL" in status_col:
                # Re-classify
                result = classify_address(addr_str)
                
                if result:
                    # Update row
                    new_class = result['class']
                    new_type = result['type']
                    # Keep source if present, or update? usually just keep or 're-validated'
                    source = row[3] if len(row) > 3 else "re-validated"
                    
                    rows.append([addr_str, new_class, new_type, source])
                    fixed_count += 1
                else:
                    # Still unknown or failed? Keep as is or mark manual?
                    # If classify_address returns None, it usually means it didn't match known streets.
                    # We keep it but maybe tag it?
                    rows.append(row)
            else:
                rows.append(row)

    print(f"Fixed {fixed_count} rows.")
    
    # Write back
    with open(TEMP_FILE, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(rows)
        
    # Replace original
    os.replace(TEMP_FILE, VALIDATION_FILE)

if __name__ == "__main__":
    fix_unknowns()
