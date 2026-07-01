import csv
import re

RISK_STREETS = [
    'SULLIVANT AVE', 'HARRISBURG PIKE', 'GREENLAWN AVE', 'W BROAD ST', 
    'STIMMEL RD', 'MCKINLEY AVE', 'CENTRAL AVE', 'W MOUND ST', 
    'W RICH ST', 'FRANK RD', 'HARMON AVE', 'EAKIN RD'
]

input_file = 'addresses_43223_formatted.csv'
output_file = 'risk_review_list.txt'

with open(input_file, 'r') as f_in, open(output_file, 'w') as f_out:
    reader = csv.reader(f_in)
    next(reader)
    
    for row in reader:
        addr = row[0]
        upper = addr.upper()
        for s in RISK_STREETS:
            if s in upper:
                f_out.write(addr + '\n')
                break

print(f"Extracted addresses to {output_file}")
