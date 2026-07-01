import csv

risk_streets = [
    'SULLIVANT AVE', 'HARRISBURG PIKE', 'GREENLAWN AVE', 'W BROAD ST', 
    'STIMMEL RD', 'MCKINLEY AVE', 'CENTRAL AVE'
]

counts = {s: 0 for s in risk_streets}

with open('addresses_43223_formatted.csv', 'r') as f:
    for line in f:
        upper = line.upper()
        for s in risk_streets:
            if s in upper:
                counts[s] += 1

print("Risk Street Counts:")
for s, c in counts.items():
    print(f"{s}: {c}")
