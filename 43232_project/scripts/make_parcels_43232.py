#!/usr/bin/env python3
"""Filter Franklin County auditor parcel data to ZIP 43232 -> parcels_43232.csv.

The full shared/data/franklin_county_parcels.csv (~485k rows, all of Franklin
County) is the snapshot source. We subset to ZIPCODE == 43232 (~13k parcels)
so parcel matching stays fast and lean, mirroring the 43213/43068 projects.
"""
import csv
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, '..', 'data')
PARCELS_FULL = '/Users/kevinpatel/Address/shared/data/franklin_county_parcels.csv'
OUT = os.path.join(DATA_DIR, 'parcels_43232.csv')
ZIP = '43232'


def main():
    os.makedirs(DATA_DIR, exist_ok=True)
    n = 0
    with open(PARCELS_FULL, newline='', encoding='utf-8-sig') as fin, \
         open(OUT, 'w', newline='') as fout:
        reader = csv.DictReader(fin)
        writer = csv.DictWriter(fout, fieldnames=reader.fieldnames)
        writer.writeheader()
        for row in reader:
            if (row.get('ZIPCODE') or '').strip() == ZIP:
                writer.writerow(row)
                n += 1
    print(f'Parcels in {ZIP}: {n} -> {OUT}')


if __name__ == '__main__':
    main()
