import csv
import re

INPUT_FILE = 'output/manual_review_needed.txt'
OUTPUT_FILE = 'output/validation_results_43026.csv'
EXCLUDED_FILE = 'output/excluded_addresses.csv'
REMAINING_FILE = 'output/manual_review_remaining.txt'

# Explicitly verified apartment buildings/complexes
APARTMENT_COMPLEX_ROOTS = [
    '5204 BRIDEWELL ST',
    '5240 FRANKLIN ST',
    '5214 BRIDEWELL ST'
]

def main():
    print("Finalizing Batch 8 Manual Review...")
    
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
            
            # 1. Approve Explicit Apartment Complexes (and their units)
            is_apartment = False
            for root in APARTMENT_COMPLEX_ROOTS:
                if clean_addr.startswith(root):
                    writer.writerow([addr, 'Residential', 'Apartment', 'Auto-Approved Batch 8 Final'])
                    approved_count += 1
                    is_apartment = True
                    break
            if is_apartment:
                continue

            # 2. General Apartment/Unit Check
            if 'APT' in clean_addr or 'UNIT' in clean_addr:
                 writer.writerow([addr, 'Residential', 'Apartment', 'Auto-Approved Batch 8 Final'])
                 approved_count += 1
                 continue

            # 3. Explicit Exclusions (based on search history/context)
            # Edwards Farms Rd 4949 and 4999 are commercial/industrial
            if clean_addr.startswith('4949 EDWARDS FARMS RD') or clean_addr.startswith('4999 EDWARDS FARMS RD'):
                writer_ex.writerow([addr, 'Commercial/Industrial'])
                excluded_count += 1
                continue
                
            # 4. Previously Verified Residential Streets (Safety Net)
            # Sometimes things slip into manual review if street extraction wasn't perfect or if they were flagged 'Mixed' mistakenly
            # Adding NIAGARA DR check
            if 'NIAGARA DR' in clean_addr:
                 writer.writerow([addr, 'Residential', 'Single Family', 'Auto-Approved Batch 8 Final'])
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
