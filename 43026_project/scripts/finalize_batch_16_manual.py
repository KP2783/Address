import csv
import os

PROJECT_ROOT = '/Users/kevinpatel/Address/43026_project'
MANUAL_FILE = os.path.join(PROJECT_ROOT, 'output', 'manual_review_needed.txt')
RESULTS_FILE = os.path.join(PROJECT_ROOT, 'output', 'validation_results_43026.csv')
EXCLUDED_FILE = os.path.join(PROJECT_ROOT, 'output', 'excluded_addresses.csv')

def finalize_batch():
    if not os.path.exists(MANUAL_FILE):
        print("No manual review file found.")
        return

    with open(MANUAL_FILE, 'r') as f:
        lines = f.readlines()

    approved = []
    excluded = []
    remaining = []

    for line in lines:
        addr = line.strip()
        if not addr: continue
        
        # Explicit Commercial Patterns on Mixed Streets
        if ' STE ' in addr.upper() or ' SUITE ' in addr.upper() or ' UNIT ' in addr.upper():
             excluded.append({'address': addr, 'reason': 'Commercial Unit on Mixed Street'})
        elif ' CATV' in addr.upper() or ' VRAD' in addr.upper() or ' ATM' in addr.upper():
             excluded.append({'address': addr, 'reason': 'Utility/Non-Residential'})
        else:
             remaining.append(addr)

    # Append to files
    if approved:
        with open(RESULTS_FILE, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['address', 'classification', 'property_type', 'source'])
            for item in approved:
                writer.writerow(item)
    
    if excluded:
        with open(EXCLUDED_FILE, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            for item in excluded:
                writer.writerow([item['address'], item['reason']])

    # Update manual review file
    with open(MANUAL_FILE, 'w') as f:
        for item in remaining:
            f.write(item + "\n")

    print(f"Finalized Batch 16. Approved: {len(approved)}, Excluded: {len(excluded)}, Remaining: {len(remaining)}")

if __name__ == "__main__":
    finalize_batch()
