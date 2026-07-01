import csv
import re

INPUT_FILE = 'output/manual_review_needed.txt'
OUTPUT_FILE = 'output/validation_results_43026.csv'
EXCLUDED_FILE = 'output/excluded_addresses.csv'
REMAINING_FILE = 'output/manual_review_remaining.txt'

def main():
    print("Finalizing Batch 11 Manual Review...")
    
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
            
            # --- Exclusions ---
            # 5608, 5604, 5612 RENNER RD -> Commercial/Ambiguous
            if '5608 RENNER RD' in clean_addr or '5604 RENNER RD' in clean_addr or '5612 RENNER RD' in clean_addr:
                writer_ex.writerow([addr, 'Commercial/Ambiguous'])
                excluded_count += 1
                continue

             # 5584 RENNER RD -> Residential (Townhome)
            if '5584 RENNER RD' in clean_addr:
                 writer.writerow([addr, 'Residential', 'Townhome', 'Auto-Approved Batch 11 Final'])
                 approved_count += 1
                 continue

            # HAYDEN'S RESERVE WAY 2
            if 'HAYDEN\'S RESERVE WAY 2' in clean_addr:
                writer.writerow([addr, 'Residential', 'Condo', 'Auto-Approved Batch 11 Final'])
                approved_count += 1
                continue
            
            # COSGRAY
            if 'COSGRAY' in clean_addr:
                writer.writerow([addr, 'Residential', 'Single Family', 'Auto-Approved Batch 11 Final'])
                approved_count += 1
                continue

            # DAVIDSON RD - Approving range 5200-5600 generally residential except school (5100)
            # We already excluded 5100.
            # 5454, 5521, 56xx -> Residential
            if 'DAVIDSON RD' in clean_addr:
                 # Check for known non-res if any? 5100 was main one.
                 # Conservatively, let's look for known residential blocks.
                 match = re.search(r'^\d+', clean_addr)
                 if match:
                     num = int(match.group())
                     if 5200 <= num <= 5800:
                         writer.writerow([addr, 'Residential', 'Single Family', 'Auto-Approved Batch 11 Final'])
                         approved_count += 1
                         continue

            # CEMETERY RD - Mixed, keep as remaining mostly.
            
            # BUCKEYE AVE - Mixed, keep as remaining.

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
