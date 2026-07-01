import csv
import re

INPUT_FILE = 'output/manual_review_needed.txt'
OUTPUT_FILE = 'output/validation_results_43026.csv'
EXCLUDED_FILE = 'output/excluded_addresses.csv'
REMAINING_FILE = 'output/manual_review_remaining.txt'

def main():
    print("Finalizing Batch 10 Manual Review...")
    
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
            if 'WESTCHESTER WOODS BLVD' in clean_addr:
                writer_ex.writerow([addr, 'Commercial/Mixed'])
                excluded_count += 1
                continue
                
            if '4500 HICKORY CHASE WAY' in clean_addr: # Library
                writer_ex.writerow([addr, 'Institutional - Library'])
                excluded_count += 1
                continue

            if '4504 HICKORY CHASE WAY' in clean_addr or '4510 HICKORY CHASE WAY' in clean_addr or '4582 HICKORY CHASE WAY' in clean_addr: # Land/Commercial
                 writer_ex.writerow([addr, 'Commercial/Land'])
                 excluded_count += 1
                 continue

            if '5100 DAVIDSON RD' in clean_addr: # High School
                writer_ex.writerow([addr, 'Institutional - School'])
                excluded_count += 1
                continue
            
            if '5375 GRACE ST' in clean_addr: # Institutional Use
                writer_ex.writerow([addr, 'Institutional - LifeWise'])
                excluded_count += 1
                continue

            if '5526 RENNER RD' in clean_addr: # Goodwill
                writer_ex.writerow([addr, 'Commercial - Retail'])
                excluded_count += 1
                continue

            if '5488 1/2 ROBERTS RD' in clean_addr or '5488 ROBERTS RD' in clean_addr: # Commercial
                writer_ex.writerow([addr, 'Commercial'])
                excluded_count += 1
                continue

            # --- Approvals ---
            if '5401 MADISON ST' in clean_addr:
                writer.writerow([addr, 'Residential', 'Apartment', 'Auto-Approved Batch 10 Final'])
                approved_count += 1
                continue
            
            if '4522 HICKORY CHASE WAY' in clean_addr: # Verena Senior Living
                writer.writerow([addr, 'Residential', 'Apartment', 'Auto-Approved Batch 10 Final'])
                approved_count += 1
                continue

            if '5380 GRACE ST' in clean_addr or '5383 GRACE ST' in clean_addr:
                writer.writerow([addr, 'Residential', 'Single Family', 'Auto-Approved Batch 10 Final'])
                approved_count += 1
                continue

            if '5454 DAVIDSON RD' in clean_addr:
                writer.writerow([addr, 'Residential', 'Single Family', 'Auto-Approved Batch 10 Final'])
                approved_count += 1
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
