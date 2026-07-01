
import csv
import sys
import concurrent.futures
import time
import random
from googlesearch import search

# Keywords for classification
RESIDENTIAL_KEYWORDS = ['single family', 'detached', 'residential', 'house', 'home']
CONDO_KEYWORDS = ['condo', 'condominium', 'townhouse', 'townhome']
APARTMENT_KEYWORDS = ['apartment', 'multifamily', 'multi-family', 'units', 'complex']
COMMERCIAL_KEYWORDS = ['commercial', 'office', 'retail', 'industrial', 'business', 'store', 'shop']
LAND_KEYWORDS = ['land', 'lot', 'vacant']

def classify_text(text):
    text = text.lower()
    if any(k in text for k in APARTMENT_KEYWORDS):
        return 'Apartment'
    if any(k in text for k in CONDO_KEYWORDS):
        return 'Condo'
    if any(k in text for k in COMMERCIAL_KEYWORDS):
        return 'Commercial'
    if any(k in text for k in LAND_KEYWORDS):
        return 'Land'
    if any(k in text for k in RESIDENTIAL_KEYWORDS):
        return 'Single Family'
    return 'Unknown'

def analyze_street(street):
    query = f"{street} Hilliard OH 43026 property type"
    print(f"Searching for: {street}")
    try:
        results = search(query, num_results=3, advanced=True)
        # Combine snippets
        full_text = ""
        for r in results:
            full_text += f"{r.title} {r.description} "
        
        classification = classify_text(full_text)
        return street, classification, full_text[:200].replace('\n', ' ')
    except Exception as e:
        print(f"Error searching {street}: {e}")
        return street, "Error", str(e)

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 identify_street_types.py <input_streets_file>")
        sys.exit(1)
        
    input_file = sys.argv[1]
    output_file = '../output/street_classifications.csv'
    
    with open(input_file, 'r') as f:
        streets = [line.strip() for line in f if line.strip()]
        
    print(f"Loaded {len(streets)} streets.")
    
    results = []
    # Use ThreadPoolExecutor for parallel searches
    # Be careful with rate limits if requests are too fast, but googlesearch might handle some.
    # We'll use a small number of workers to be safe.
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        future_to_street = {executor.submit(analyze_street, street): street for street in streets}
        
        for i, future in enumerate(concurrent.futures.as_completed(future_to_street)):
            street = future_to_street[future]
            try:
                res = future.result()
                results.append(res)
                print(f"[{i+1}/{len(streets)}] Classified {street} -> {res[1]}")
            except Exception as e:
                print(f"Exception for {street}: {e}")
                results.append((street, "Error", str(e)))
            
            # small sleep to avoid completely hammering
            time.sleep(1)

    # Save to CSV
    with open(output_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Street', 'Classification', 'Snippet'])
        writer.writerows(results)
        
    print(f"Saved results to {output_file}")

if __name__ == "__main__":
    main()
