
import csv
import concurrent.futures
import time
import re
import sys
import random

try:
    from googlesearch import search
except ImportError:
    print("No googlesearch found, will use mock or fail.")

RESIDENTIAL_KEYWORDS = ['single family', 'condo', 'apartment', 'townhome', 'residential', 'home']
COMMERCIAL_KEYWORDS = ['retail', 'office', 'medical', 'commercial', 'store', 'industrial', 'business', 'government', 'municipal', 'church', 'school']

def classify_text(text):
    text = text.lower()
    for k in RESIDENTIAL_KEYWORDS:
        if k in text:
            return 'Residential'
    for k in COMMERCIAL_KEYWORDS:
        if k in text:
            return 'Commercial' # Exclude
    return 'Unknown'

def google_verify_address(address):
    query = f"{address} property type"
    print(f"Searching: {query}")
    try:
        results = search(query, num_results=3, advanced=True)
        text = ""
        for r in results:
            text += f"{r.title} {r.description} "
        
        classification = classify_text(text)
        return classification, text
    except Exception as e:
        print(f"Error searching {address}: {e}")
        return 'Unknown', str(e)

def resolve_manuals():
    input_file = 'output/manual_review_needed.txt'
    res_file = 'output/validation_results_43026.csv'
    exc_file = 'output/excluded_addresses.csv'
    unknown_file = 'output/final_unknowns_batch3.csv'

    addresses = []
    with open(input_file, 'r') as f:
        for line in f:
            if line.strip():
                addresses.append(line.strip())

    print(f"Loaded {len(addresses)} addresses to resolve.")

    resolved_res = []
    resolved_exc = []
    needs_search = []

    for addr in addresses:
        street_search = re.search(r'^\d+\s+(.*?),', addr)
        if not street_search:
            needs_search.append(addr)
            continue
        
        street = street_search.group(1).upper()
        # Handle unit info in street name if regex failed to catch it cleanly, 
        # but my regex in extract_streets usually handles it. 
        # Here we just check substrings.

        if 'HERITAGE CLUB DR' in street:
            resolved_res.append([addr, 'Residential', 'Apartment/Community'])
        elif 'MUNICIPAL WAY' in street:
            resolved_exc.append([addr, 'Government', 'Bulk_Rule'])
        elif 'SCHIRTZINGER RD' in street:
            resolved_res.append([addr, 'Residential', 'Single Family (Verified)'])
        elif 'SMILEY RD' in street:
            resolved_res.append([addr, 'Residential', 'Single Family (Verified)'])
        elif 'TRUEMAN CT' in street:
            resolved_exc.append([addr, 'Commercial', 'Medical/Office'])
        elif 'VETERANS MEMORIAL DR' in street:
            resolved_exc.append([addr, 'Government', 'Park/Govt'])
        elif 'PARK MILL RUN DR' in street:
            resolved_exc.append([addr, 'Commercial', 'Retail/Mixed'])
        elif 'CEMETERY RD' in street: # Usually commercial on this main strip
             # Check if any Residential exists? Most are commercial. 
             # Let's search Cemetery Rd to be safe, or just exclude if high confidence.
             # I'll search it.
             needs_search.append(addr)
        else:
            needs_search.append(addr)

    print(f"Auto-resolved {len(resolved_res)} Residential, {len(resolved_exc)} Excluded.")
    print(f"Searching {len(needs_search)} addresses...")

    # Run searches
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        future_to_addr = {executor.submit(google_verify_address, addr): addr for addr in needs_search}
        
        for future in concurrent.futures.as_completed(future_to_addr):
            addr = future_to_addr[future]
            try:
                cls, text = future.result()
                if cls == 'Residential':
                    resolved_res.append([addr, 'Residential', 'Google_Verify'])
                elif cls == 'Commercial':
                    resolved_exc.append([addr, 'Commercial', 'Google_Verify'])
                else:
                    # Unknown
                    # For now, dump to unknown file
                     with open(unknown_file, 'a') as f:
                        f.write(f"{addr},Unknown,{text[:100]}\n")
            except Exception as e:
                print(f"Failed {addr}: {e}")
            time.sleep(1)

    # Write outputs
    with open(res_file, 'a', newline='') as f:
        writer = csv.writer(f)
        for row in resolved_res:
            writer.writerow(row)
            
    with open(exc_file, 'a', newline='') as f:
        writer = csv.writer(f)
        for row in resolved_exc:
            writer.writerow(row)

    print("Done.")

if __name__ == "__main__":
    resolve_manuals()
