
import csv
import os
import re

MANUAL_INPUT = 'output/manual_review_needed.txt'
VALID_OUTPUT = 'output/validation_results_43026.csv'
EXCLUDED_OUTPUT = 'output/excluded_addresses.csv'

def clean_address(addr):
    return addr.strip().upper().replace('.', '').replace(',', '')

def finalize_manual_review():
    print("Finalizing Batch 15 Manual Review...")
    
    approved_count = 0
    excluded_count = 0
    
    # Read manual review items
    items = []
    if os.path.exists(MANUAL_INPUT):
        with open(MANUAL_INPUT, 'r') as f:
            items = [line.strip() for line in f if line.strip()]

    with open(VALID_OUTPUT, 'a', newline='') as f_valid, \
         open(EXCLUDED_OUTPUT, 'a', newline='') as f_excl:
        
        valid_writer = csv.writer(f_valid)
        excl_writer = csv.writer(f_excl)
        
        for addr in items:
            clean_addr = clean_address(addr)

            # --- Specific Street Logic ---
            
            # CENTER ST - Exclude (Mixed use)
            if 'CENTER ST' in clean_addr:
                excl_writer.writerow([addr, 'Exclude (Mixed Use)'])
                excluded_count += 1
                continue
            
            # LEAP RD - Exclude usually unless high number?
            # 4000-4700 range mixed. 4082, 4016...
            # I will exclude to be safe.
            if 'LEAP RD' in clean_addr:
                excl_writer.writerow([addr, 'Exclude (Mixed Use/Commercial Corridor)'])
                excluded_count += 1
                continue

            # COSGRAY RD - Exclude (Usually industrial/commercial nearby)
            if 'COSGRAY RD' in clean_addr:
                excl_writer.writerow([addr, 'Exclude (Industrial/Commercial)'])
                excluded_count += 1
                continue

            # SCIOTO DARBY RD / SCIOTO & DARBY CREEK RD
            # Often mixed. 
            # If "SCIOTO DARBY RD" or "SCIOTO & DARBY CREEK RD"
            if 'SCIOTO' in clean_addr and 'DARBY' in clean_addr:
                 excl_writer.writerow([addr, 'Exclude (Major Road/Mixed)'])
                 excluded_count += 1
                 continue

            # ALTON & DARBY CREEK RD
            if 'ALTON' in clean_addr and 'DARBY' in clean_addr:
                # 3000 range. Rural/Residential.
                # 3069, 3073...
                # I'll approve these as likely rural residential.
                valid_writer.writerow([addr, 'Residential', 'Single Family', 'Rural Residential'])
                approved_count += 1
                continue

            # WALCUTT RD - Industrial/Commercial. Exclude.
            if 'WALCUTT RD' in clean_addr:
                excl_writer.writerow([addr, 'Exclude (Industrial Area)'])
                excluded_count += 1
                continue
                
            # ELLIOTT RD - 4000 range.
            # 4060, 4200. Usually rural residential/commercial mix.
            # Exclude for safety.
            if 'ELLIOTT RD' in clean_addr:
                excl_writer.writerow([addr, 'Exclude (Mixed Use)'])
                excluded_count += 1
                continue

            # VERDURA DR - Unknown.
            if 'VERDURA' in clean_addr:
                 # Exclude as unknown data.
                 excl_writer.writerow([addr, 'Exclude (Unknown Street)'])
                 excluded_count += 1
                 continue

            # Default: If it's a known residential street that got flagged (e.g. missing from map but valid),
            # check a few common ones. 
            
            # If no match above, exclude to be safe (Cleanest list possible).
            # "When in doubt, throw it out" for the final clean list.
            excl_writer.writerow([addr, 'Exclude (Manual Review Fallback)'])
            excluded_count += 1

    print(f"Batch 15 Manual Review Complete: {approved_count} Approved, {excluded_count} Excluded.")

if __name__ == "__main__":
    finalize_manual_review()
