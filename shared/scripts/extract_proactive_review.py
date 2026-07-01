import csv

TARGET_STREETS = ['CLIME RD', 'BROWN RD', 'HARRISBURG PIKE']

with open('addresses_43223_formatted.csv', 'r') as f_in, open('review_streets_proactive.txt', 'w') as f_out:
    reader = csv.reader(f_in)
    next(reader)
    for row in reader:
        addr = row[0]
        upper = addr.upper()
        for street in TARGET_STREETS:
            if street in upper:
                f_out.write(addr + '\n')
                break
