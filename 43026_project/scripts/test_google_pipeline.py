
import sys
import os
import csv

# Add local directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from batch_validate_43026 import process_search_result, save_results

# Define 5 samples with their search results
samples = [
    {
        "address": "1531 WHISPERING WILLOW LN, Columbus, OH, 43026",
        "result": """The address 1531 Whispering Willow Lane, Columbus, OH 43026...
        Source: zillow.com"""
    },
    {
        "address": "1543 WHISPERING WILLOW LN, Columbus, OH, 43026",
        "result": """I could not find specific details for the address 1543 Whispering Willow Ln, Columbus, OH, 43026 in the search results. However, there is a listing for 1531 Whispering Willow Ln, Columbus, OH 43026, which was previously available for rent."""
    },
    {
        "address": "1544 BENDING WILLOW LN, Columbus, OH, 43026",
        "result": """I couldn't find an exact match for "1544 BENDING WILLOW LN, Columbus, OH, 43026" in my search. However, I found some related information that might be helpful:
*   There is an affordable housing community named "Willow Bend" located at 1531 Whispering Willow Ln..."""
    },
    {
        "address": "1545 WHISPERING WILLOW LN, Columbus, OH, 43026",
        "result": """Based on the information found, an address similar to the one provided, 1531 Whispering Willow Ln, is located in Hilliard, OH 43026...
No direct information was found for "1545 Whispering Willow Ln, Columbus, OH, 43026" as a distinct residential property."""
    },
    {
        "address": "1550 BENDING WILLOW LN, Columbus, OH, 43026",
        "result": """The address "1550 BENDING WILLOW LN, Columbus, OH, 43026" appears to be closely associated with the Willow Bend Apartments, which are officially located at 1531 Whispering Willow Lane, Hilliard, OH 43026. While the street number and name are slightly different, Hilliard is a suburb of Columbus..."""
    }
]

validation_results = []

print("Processing samples...")
for sample in samples:
    val = process_search_result(sample['address'], sample['result'])
    val['search_snippet'] = sample['result'][:200]
    validation_results.append(val)
    print(f"Processed {sample['address']}: {val['classification']}")

print("\nSaving results to CSV...")
save_results(validation_results)

print("\nDone.")
