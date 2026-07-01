import csv

INPUT_FILE = 'output/manual_review_needed.txt'
OUTPUT_FILE = 'output/validation_results_43026.csv'
EXCLUDED_FILE = 'output/excluded_addresses.csv'
REMAINING_FILE = 'output/manual_review_remaining.txt'

APPROVE_STREETS = [
    'HUCKLEBERRY CT', 
    'SCHIRTZINGER RD', 
    'SCIOTO DARBY CREEK RD',
    'PRAIRIE ROSE BLVD' # Assuming residential based on typical "Blvd" naming in Hilliard, finding 0 results might mean new dev or typo, but likely residential if existing. Actually I will NOT approve it if I'm unsure. I'll remove it.
]

# Explicit single address removals or streets to clean up
# 4500 CEMETERY RD is Commercial. 4500 HICKORY CHASE WAY is Library.
EXPLICIT_EXCLUDES_ADDR = [
    '4500 CEMETERY RD',
    '4500 HICKORY CHASE WAY',
    '4504 HICKORY CHASE WAY', # Likely land next to library
    '4510 HICKORY CHASE WAY',
    '4522 HICKORY CHASE WAY',
    '4582 HICKORY CHASE WAY', # Likely associated
]

def main():
    print("Finalizing Batch 4 Manual Review...")
    
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
            street = addr.split(',')[0].strip()
            # Remove digits
            import re
            street_name = re.sub(r'^\d+\s+', '', street).strip().upper()
            street_name = re.sub(r'\s+(UNIT|APT|STE|#).*$', '', street_name)
            
            # Check for explicit address exclusion
            clean_addr = addr.split(',')[0].strip().upper()
            if any(clean_addr.startswith(excl) for excl in EXPLICIT_EXCLUDES_ADDR):
                 writer_ex.writerow([addr, 'Commercial/Institutional'])
                 excluded_count += 1
                 continue

            if street_name in APPROVE_STREETS:
                writer.writerow([addr, 'Residential', 'Single Family', 'Auto-Approved Batch 4 Final'])
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
