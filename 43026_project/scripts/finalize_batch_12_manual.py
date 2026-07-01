import csv
import re

INPUT_FILE = 'output/manual_review_needed.txt'
OUTPUT_FILE = 'output/validation_results_43026.csv'
EXCLUDED_FILE = 'output/excluded_addresses.csv'
REMAINING_FILE = 'output/manual_review_remaining.txt'

def main():
    print("Finalizing Batch 12 Manual Review...")
    
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
            
            # --- Approvals ---

            # VILLAGE BRIDGE DR (G1...G9) -> Residential Condo
            if 'VILLAGE BRIDGE DR' in clean_addr:
                 writer.writerow([addr, 'Residential', 'Condo', 'Auto-Approved Batch 12 Final'])
                 approved_count += 1
                 continue

            # HAYDEN RUN RD - Specific Verified Items
            if '5700 HAYDEN RUN RD' in clean_addr or \
               '5801 HAYDEN RUN RD' in clean_addr or \
               '5813 HAYDEN RUN RD' in clean_addr:
                writer.writerow([addr, 'Residential', 'Single Family', 'Auto-Approved Batch 12 Final'])
                approved_count += 1
                continue
            
            # DAVIDSON RD - Approving range 5200-5800
            if 'DAVIDSON RD' in clean_addr:
                 match = re.search(r'^\d+', clean_addr)
                 if match:
                     num = int(match.group())
                     # 5100 is school, excluded. 5200+ seems residential.
                     if 5200 <= num <= 5800:
                         writer.writerow([addr, 'Residential', 'Single Family', 'Auto-Approved Batch 12 Final'])
                         approved_count += 1
                         continue

            # --- Exclusions ---

            # 5730 HAYDEN RUN RD -> Commercial (Auto Repair)
            if '5730 HAYDEN RUN RD' in clean_addr:
                writer_ex.writerow([addr, 'Commercial/Auto Repair'])
                excluded_count += 1
                continue

            # --- Remaining ---
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
