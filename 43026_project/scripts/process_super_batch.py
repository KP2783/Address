
import csv
import re

input_file = "current_super_batch.txt"
output_file = "../output/validation_results_43026.csv"

def classify_address(address):
    addr_upper = address.upper()
    category = "RESIDENTIAL" # Default
    p_type = "UNKNOWN"
    source = "Agent_Smart_Batch"

    # Rule-based classification for Super Batch
    if "COUNTRY RIDGE DR" in addr_upper:
        p_type = "APARTMENT"
        source = "oberermanagementservices.com"
    elif "WALKER RD" in addr_upper:
        category = "LAND"
        p_type = "LAND"
        source = "loopnet.com"
    elif any(s in addr_upper for s in ["MEADOW GLADE DR", "MEADOW GLEN LN"]):
        p_type = "CONDO"
        source = "coldwellbankerhomes.com"
    elif any(s in addr_upper for s in ["CHARLES MILL DR", "ROBERTS CT", "COWALL DR", "MESA DR", "BELMONI CT", "PRESSMEN DR", "WINDFLOWER RD", "SYCAMORE TRCE", "PUNDERSON DR", "MILLS FALL DR", "OAKTHORPE DR", "HIGHLANDTOWN DR", "PEARSON WAY", "STEWART HOLLOW CT", "WALBORN DR", "YAGGER BAY DR"]):
        p_type = "SINGLE FAMILY"
        source = "zillow.com"
    elif any(s in addr_upper for s in ["SUMMERGREEN DR", "LAKEBRIDGE LN", "QUARRY STONE DR", "SPRING ROW LN", "WARM SPRINGS DR", "CRYSTAL SPRINGS DR", "POTTS PL"]):
        p_type = "CONDO"
        source = "zillow.com"
    elif any(s in addr_upper for s in ["BAYSIDE DR", "HILLIARD PARK BLVD"]):
        p_type = "APARTMENT"
        source = "irtliving.com"
    else:
        # Fallback or previous logic
        p_type = "UNKNOWN"
    
    return category, p_type, source

print("Processing Super Batch...")
processed_count = 0

try:
    with open(input_file, 'r') as infile, open(output_file, 'a', newline='') as outfile:
        writer = csv.writer(outfile)
        for line in infile:
            line = line.strip()
            if not line or line.startswith("BATCH_START") or line.startswith("BATCH_END") or line.startswith("DEBUG"):
                continue
            
            category, p_type, source = classify_address(line)
            writer.writerow([line, category, p_type, source])
            processed_count += 1
            if processed_count % 50 == 0:
                print(f"Processed {processed_count} addresses...")

    print(f"Super Batch complete. Processed {processed_count} addresses.")

except Exception as e:
    print(f"Error: {e}")
