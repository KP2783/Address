import re

streets = set()
with open('commercial_corridor_review.txt', 'r') as f:
    for line in f:
        line = line.strip()
        # Look for lines like "CEMETERY RD - 148 addresses"
        match = re.match(r'^([A-Z0-9 ]+) - \d+ addresses', line)
        if match:
            streets.add(match.group(1))

print(sorted(list(streets)))
