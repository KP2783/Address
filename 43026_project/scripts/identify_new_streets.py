
import concurrent.futures
import time
import csv
from googlesearch import search

import sys
import os

# Add scripts dir to path to allow imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from extract_streets import extract_streets
from process_mega_batch_results import STREET_MAP

INPUT_BATCH_FILE = 'output/current_mega_batch.txt'

def get_new_streets():
    print(f"Extracting streets from {INPUT_BATCH_FILE}...")
    unique_streets = extract_streets(INPUT_BATCH_FILE)
    print(f"Found {len(unique_streets)} unique streets in batch.")
    
    new_streets = []
    for s in unique_streets:
        if s not in STREET_MAP:
            new_streets.append(s)
            
    print(f"Identified {len(new_streets)} NEW streets not in verified map.")
    return sorted(new_streets)

NEW_STREETS = [] # Placeholder, will be populated in main


def classify_text(text):
    text = text.lower()
    if any(k in text for k in ['apartment', 'community', 'rent']):
        return 'Apartment'
    if any(k in text for k in ['condo', 'condominium', 'townhome']):
        return 'Condo'
    if any(k in text for k in ['commercial', 'office', 'retail', 'business', 'industrial']):
        return 'Commercial' # Suggests mixed use
    # specific overrides
    if 'municipal' in text or 'police' in text:
        return 'Government'
    if any(k in text for k in ['single family', 'house', 'residential', 'home']):
        return 'Single Family'
    return 'Unknown'

def analyze_street(street):
    query = f"{street} Hilliard OH 43026 property type"
    print(f"Searching: {street}")
    try:
        results = search(query, num_results=3, advanced=True)
        full_text = ""
        for r in results:
            full_text += f"{r.title} {r.description} "
        
        classification = classify_text(full_text)
        # Check specific risky keywords for manual review
        if 'land' in full_text.lower() or 'lot' in full_text.lower():
             classification = 'Check_Specific'
        if 'school' in full_text.lower() or 'church' in full_text.lower():
             classification = 'Check_Specific'
             
        return street, classification, full_text[:100].replace('\n', ' ')
    except Exception as e:
        print(f"Error {street}: {e}")
        return street, "Error", str(e)

def main():
    streets_to_check = get_new_streets()
    
    if not streets_to_check:
        print("No new streets found to verify.")
        return

    results = []
    # Use ThreadPoolExecutor for parallel searches
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        future_to_street = {executor.submit(analyze_street, s): s for s in streets_to_check}
        for future in concurrent.futures.as_completed(future_to_street):
            s = future_to_street[future]
            try:
                res = future.result()
                results.append(res)
                print(f"Verified {s} -> {res[1]}")
            except Exception as e:
                print(f"Fail {s}: {e}")
                
    # Save to CSV
    with open('output/new_street_classifications.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Street', 'Classification', 'Snippet'])
        writer.writerows(results)

if __name__ == "__main__":
    main()
