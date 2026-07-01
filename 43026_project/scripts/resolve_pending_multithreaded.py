
import csv
import concurrent.futures
import time
import random
import re
from googlesearch import search

INPUT_FILE = 'output/pending_validation.txt'
OUTPUT_FILE = 'output/resolved_pending.csv'

# Keywords for classification
RESIDENTIAL_KEYWORDS = [
    'single family', 'residential', 'home', 'house', 'condo', 'apartment', 
    'townhome', 'duplex', 'multi-family', 'manufactured'
]
COMMERCIAL_KEYWORDS = [
    'commercial', 'office', 'retail', 'industrial', 'warehouse', 'store', 
    'shop', 'business', 'parking', 'vacant land', 'lot', 'acres', 'land for sale'
]
# "Land" can be residential land, but user wants "Residential Addresses". 
# Usually vacant land is excluded. 
# If snippet says "0.5 acres" it might be just land. 
# We will classify "Land" as "Invalid" for now, or flag it.

def classify_snippet(text):
    text = text.lower()
    
    # Check Commercial First
    if any(k in text for k in ['commercial', 'office', 'retail', 'industrial', 'warehouse']):
        return 'Commercial'
    
    # Check Vacant Land
    if 'vacant land' in text or 'land for sale' in text:
        return 'Land'
        
    # Check Residential
    if any(k in text for k in RESIDENTIAL_KEYWORDS):
        return 'Residential'
        
    if 'lot' in text and 'acres' in text and 'home' not in text:
         return 'Land'

    return 'Unknown'

def validate_address(address):
    query = f"{address} property type"
    print(f"Searching: {query}")
    try:
        results = search(query, num_results=3, advanced=True)
        full_text = ""
        for r in results:
            full_text += f"{r.title} {r.description} "
        
        classification = classify_snippet(full_text)
        return {
            'address': address,
            'classification': classification,
            'snippet': full_text[:200].replace('\n', ' ')
        }
    except Exception as e:
        print(f"Error searching {address}: {e}")
        return {
            'address': address,
            'classification': 'Error',
            'snippet': str(e)
        }

def main():
    addresses = []
    with open(INPUT_FILE, 'r') as f:
        for line in f:
            if line.strip():
                addresses.append(line.strip())
                
    print(f"Resolving {len(addresses)} pending addresses...")
    
    resolved_data = []
    
    # Use ThreadPoolExecutor
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        future_to_addr = {executor.submit(validate_address, addr): addr for addr in addresses}
        
        for i, future in enumerate(concurrent.futures.as_completed(future_to_addr)):
            addr = future_to_addr[future]
            try:
                res = future.result()
                resolved_data.append(res)
                print(f"[{i+1}/{len(addresses)}] {addr} -> {res['classification']}")
            except Exception as e:
                print(f"Exception for {addr}: {e}")
            
            time.sleep(random.uniform(0.5, 1.5)) # Polite delay
            
    # Write results
    with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['address', 'classification', 'snippet']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in resolved_data:
            writer.writerow(row)
            
    print(f"Finished. Results saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
