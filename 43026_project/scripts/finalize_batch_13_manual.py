import csv
import re

INPUT_FILE = 'output/manual_review_needed.txt'
OUTPUT_FILE = 'output/validation_results_43026.csv'
EXCLUDED_FILE = 'output/excluded_addresses.csv'
REMAINING_FILE = 'output/manual_review_remaining.txt'

def main():
    print("Finalizing Batch 13 Manual Review...")
    
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

            # Streets verified as fully residential in this batch check
            if 'PISELLO DR' in clean_addr or \
               'HERITAGE VIEW CT' in clean_addr or \
               'HOMESTEAD CT' in clean_addr or \
               'DEVER DR' in clean_addr or \
               'GLADE RUN RD' in clean_addr:
                writer.writerow([addr, 'Residential', 'Single Family', 'Auto-Approved Batch 13 Final'])
                approved_count += 1
                continue

            # HAYDEN RUN RD - High number range verified (5800+)
            if 'HAYDEN RUN RD' in clean_addr:
                 match = re.search(r'^\d+', clean_addr)
                 if match:
                     num = int(match.group())
                     # Verified 5899, 5909, 6015, etc. are Residential.
                     # 5730 is Commercial (Excluded). 5700, 5801, 5813 Approved in Batch 12.
                     # Approving 5800+ here.
                     if num >= 5800:
                         writer.writerow([addr, 'Residential', 'Single Family', 'Auto-Approved Batch 13 Final'])
                         approved_count += 1
                         continue

            # --- Exclusions ---

            # 5794 RENNER RD -> Ambiguous/likely invalid or non-residential
            if '5794 RENNER RD' in clean_addr:
                writer_ex.writerow([addr, 'Commercial/Ambiguous'])
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
