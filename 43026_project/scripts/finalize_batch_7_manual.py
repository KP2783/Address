import csv
import re

INPUT_FILE = 'output/manual_review_needed.txt'
OUTPUT_FILE = 'output/validation_results_43026.csv'
EXCLUDED_FILE = 'output/excluded_addresses.csv'
REMAINING_FILE = 'output/manual_review_remaining.txt'

APPROVE_STREETS = [
    'CALICO CT',
    'STANBERRY RD',
    'SCIOTO CHASE DR',
    'SINGLETON DR',
    'VICKSBURG LN',
    'VICKSBURG CT',
    'TRAVERS CT',
    'HELMSDALE DR',
    'SINGLETON DR A',
    'AMBLYN CT',
    'BANTAM CT',
    'BIGELOW DR',
    'BOMAR DR',
    'BRANDAMORE CT',
    'BRECKENHURST DR',
    'BRESSLER DR',
    'BRIDLE CREEK WAY',
    'BUTTE CT',
    'CAVALIER DR',
    'CRESTBURY CT',
    'DEVENCROFT CT',
    'DIXON DR',
    'DRIVEMERE RD',
    'FLAGSTAFF CT',
    'FOXTAIL DR',
    'GILLETTE AVE',
    'GILWOOD DR',
    'GRANDON DR',
    'GREDLE DR',
    'HAMILTON RD',
    'HARVEST MEADOW CT',
    'HAVENSIDE DR',
    'HAYDEN WOODS LN',
    'HIDDEN VIEW DR',
    'HIGHGLADE DR',
    'HIGHLAND MEADOWS DR',
    'LANGCROFT DR',
    'MEADOWFIELD LN',
    'MENGEL LN',
    'MONTCROFT DR',
    'PREFERRED PL',
    'RADSTOCK CT',
    'RENMILL DR',
    'RENMILL DR CATV',
    'RIGGINS RUN S',
    'SCALTON PL',
    'SPICE MARKET W',
    'STONECROFT CT',
    'WAYCROFT CT',
    'WYANDOT PL'
]

EXPLICIT_EXCLUDES_ADDR = [
    '5091 HAYDEN RUN RD',
    '5100 HAYDEN RUN RD',
    '5095 HAYDEN RUN RD',
    '5097 HAYDEN RUN RD',
    '5099 HAYDEN RUN RD',
    '5105 HAYDEN RUN RD',
    '4999 EDWARDS FARMS RD',
    '5101 HAYDEN RUN RD'
]

def main():
    print("Finalizing Batch 7 Manual Review...")
    
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
            for excl in EXPLICIT_EXCLUDES_ADDR:
                if clean_addr.startswith(excl): # Use startswith to catch variations
                     writer_ex.writerow([addr, 'Commercial/Institutional'])
                     excluded_count += 1
                     is_excluded = True
                     break
            if is_excluded:
                continue

            # Extract street name
            parts = clean_addr.split(',')
            street_part = parts[0].strip()
            # Remove leading numbers
            street_name = re.sub(r'^\d+\s+', '', street_part).strip()
            # Remove unit info
            street_name = re.sub(r'\s+(UNIT|APT|STE|#).*$', '', street_name).strip()
            
            if 'APT' in clean_addr or 'UNIT' in clean_addr:
                 writer.writerow([addr, 'Residential', 'Apartment', 'Auto-Approved Batch 7 Final'])
                 approved_count += 1
                 continue

            if street_name in APPROVE_STREETS:
                writer.writerow([addr, 'Residential', 'Single Family/Condo', 'Auto-Approved Batch 7 Final'])
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
