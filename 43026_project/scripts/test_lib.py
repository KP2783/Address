
from googlesearch import search

try:
    print("Searching...")
    results = search("Google", num_results=1)
    count = 0
    for r in results:
        print(f"Result: {r.title}")
        count += 1
    print(f"Found {count} results")
except Exception as e:
    print(f"Error: {e}")
