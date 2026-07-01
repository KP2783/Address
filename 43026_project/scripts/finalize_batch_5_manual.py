import csv
import re

INPUT_FILE = 'output/manual_review_needed.txt'
OUTPUT_FILE = 'output/validation_results_43026.csv'
EXCLUDED_FILE = 'output/excluded_addresses.csv'
REMAINING_FILE = 'output/manual_review_remaining.txt'

APPROVE_STREETS = [
    'SCHIRTZINGER RD', 
    'DAVIDSON RD',
    'CLUBPARK DV', # Verified Condo typo
]

# Explicit exclusions if known
EXPLICIT_EXCLUDES_ADDR = [
    '4500 HICKORY CHASE WAY',
    '4504 HICKORY CHASE WAY',
    '4510 HICKORY CHASE WAY',
    '4522 HICKORY CHASE WAY',
    '4582 HICKORY CHASE WAY',
]

def main():
    print("Finalizing Batch 5 Manual Review...")
    
    addresses = []
    try:
        with open(INPUT_FILE, 'r') as f:
            addresses = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print("No manual review file found.")
        return

    approved_count = 0
    excluded_count = 0
    remaining = []

    with open(OUTPUT_FILE, 'a', newline='') as f_out, open(EXCLUDED_FILE, 'a', newline='') as f_ex:
        writer = csv.writer(f_out)
        writer_ex = csv.writer(f_ex)
        
        for addr in addresses:
            clean_addr = addr.upper().strip()
            
            # Extract street name
            parts = clean_addr.split(',')
            street_part = parts[0].strip()
            street_name = re.sub(r'^\d+\s+', '', street_part).strip()
            street_name = re.sub(r'\s+(UNIT|APT|STE|#).*$', '', street_name).strip()

            # Check for explicit address exclusion
            if any(clean_addr.startswith(excl) for excl in EXPLICIT_EXCLUDES_ADDR):
                 writer_ex.writerow([addr, 'Commercial/Institutional'])
                 excluded_count += 1
                 continue

            if street_name in APPROVE_STREETS:
                writer.writerow([addr, 'Residential', 'Single Family/Condo', 'Auto-Approved Batch 5 Final'])
                approved_count += 1
            else:
                remaining.append(addr)

    # Write remaining
    with open(REMAINING_FILE, 'w') as f:
        for item in remaining:
            f.write(f"{item}\n")

    print(f"Approved: {approved_count}")
    print(f"Excluded: {excluded_count}")
    print(f"Remaining: {len(remaining)}")

if __name__ == "__main__":
    main()
