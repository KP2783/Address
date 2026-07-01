import csv
import re

INPUT_FILE = 'output/manual_review_needed.txt'
OUTPUT_FILE = 'output/validation_results_43026.csv'
EXCLUDED_FILE = 'output/excluded_addresses.csv'
REMAINING_FILE = 'output/manual_review_remaining.txt'

# Single Family Streets to Approve
APPROVE_STREETS = [
    'GWINNETT CIR'
]

# Explicitly verified apartment buildings/complexes
APARTMENT_COMPLEX_ROOTS = [
    '5240 FRANKLIN ST',
    '5315 CATALINA CIRCLE DR',
    '5319 CATALINA CIRCLE DR',
    '5204 BRIDEWELL ST'
]

def main():
    print("Finalizing Batch 9 Manual Review...")
    
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
            
            # Helper for explicit checks
            is_excluded = False
            if '5370 GRACE ST' in clean_addr:
                 writer_ex.writerow([addr, 'Commercial/Tax Exempt'])
                 excluded_count += 1
                 continue

            # 1. Approve Explicit Apartment Complexes (and their units)
            is_apartment = False
            for root in APARTMENT_COMPLEX_ROOTS:
                if clean_addr.startswith(root):
                    writer.writerow([addr, 'Residential', 'Apartment', 'Auto-Approved Batch 9 Final'])
                    approved_count += 1
                    is_apartment = True
                    break
            if is_apartment:
                continue

            # 2. General Apartment/Unit Check
            if 'APT' in clean_addr or 'UNIT' in clean_addr:
                 writer.writerow([addr, 'Residential', 'Apartment', 'Auto-Approved Batch 9 Final'])
                 approved_count += 1
                 continue

            # 3. Approve Streets
            # Extract street name
            parts = clean_addr.split(',')
            street_part = parts[0].strip()
            street_name = re.sub(r'^\d+\s+', '', street_part).strip()
            street_name = re.sub(r'\s+(UNIT|APT|STE|#).*$', '', street_name).strip()

            if street_name in APPROVE_STREETS:
                writer.writerow([addr, 'Residential', 'Single Family', 'Auto-Approved Batch 9 Final'])
                approved_count += 1
                continue

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
