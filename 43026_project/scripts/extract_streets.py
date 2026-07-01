
import re

def extract_streets(filename):
    streets = set()
    try:
        with open(filename, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("DEBUG") or line.startswith("BATCH"):
                    continue
                # Extract street name (Available format: "123 MAIN ST, City, State, Zip")
                # We assume standard format.
                parts = line.split(',')
                if len(parts) >= 1:
                    address_part = parts[0].strip()
                    # Remove house number (digits at start)
                    street = re.sub(r'^\d+\s+', '', address_part).strip()
                    # Remove unit numbers if any (simple heuristic)
                    street = re.sub(r'\s+(UNIT|APT|STE|#).*$', '', street, flags=re.IGNORECASE)
                    # Normalize
                    streets.add(street.upper())
    except Exception as e:
        print(f"Error: {e}")
        return []

    return sorted(list(streets))

if __name__ == "__main__":
    import sys
    filename = 'current_mega_batch.txt'
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    
    unique_streets = extract_streets(filename)
    for s in unique_streets:
        print(s)
