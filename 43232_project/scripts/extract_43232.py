#!/usr/bin/env python3
"""Extract 43232 addresses from Franklin County GeoJSON.

Streams oh/franklin-addresses-county.geojson (line-delimited Features), keeps
postcode == 43232, dedups on (number|street|unit), drops incomplete rows.
Outputs a raw structured CSV (input to parcel matching) and a formatted
single-column CSV (keyword commercial-filter applied, for reference).

43232 is Columbus / Franklin County — single source, no boundary merge.
"""
import csv
import json
import os
import re
from collections import Counter

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, '..', 'data')
ZIP = '43232'
CITY_DEFAULT = 'Columbus'

GEOJSON = '/Users/kevinpatel/Address/oh/franklin-addresses-county.geojson'
OUT_RAW = os.path.join(DATA_DIR, f'addresses_{ZIP}.csv')
OUT_FMT = os.path.join(DATA_DIR, f'addresses_{ZIP}_formatted.csv')

COMMERCIAL_UNITS = ['STE', 'SUITE', 'FLOOR', 'FL', 'LOBBY', 'OFFICE', 'OFC', 'BLDG', 'DEPT']
COMMERCIAL_STREETS = ['PLAZA', 'MALL', 'INDUSTRIAL', 'COMMERCE', 'CORPORATE']


def is_commercial(row):
    unit = (row.get('unit') or '').upper()
    street = (row.get('street') or '').upper()
    return any(c in unit for c in COMMERCIAL_UNITS) or any(c in street for c in COMMERCIAL_STREETS)


def main():
    os.makedirs(DATA_DIR, exist_ok=True)
    addresses = []
    seen = set()
    scanned = 0
    with open(GEOJSON, 'r') as f:
        for line in f:
            scanned += 1
            line = line.strip()
            if not line:
                continue
            try:
                feat = json.loads(line)
            except json.JSONDecodeError:
                continue
            props = feat.get('properties', {})
            if (props.get('postcode') or '').strip() != ZIP:
                continue
            number = (props.get('number') or '').strip()
            street = re.sub(r'\s+', ' ', (props.get('street') or '')).strip()
            if not number or not street:
                continue
            unit = (props.get('unit') or '').strip()
            city = (props.get('city') or CITY_DEFAULT).strip() or CITY_DEFAULT
            region = (props.get('region') or 'OH').strip()
            coords = feat.get('geometry', {}).get('coordinates', [0, 0])
            lon, lat = (coords + [0, 0])[0], (coords + [0, 0])[1]
            key = f'{number}|{street}|{unit}'
            if key in seen:
                continue
            seen.add(key)
            addresses.append({
                'number': number, 'street': street, 'unit': unit,
                'city': city, 'region': region, 'postcode': ZIP,
                'latitude': lat, 'longitude': lon,
            })

    fields = ['number', 'street', 'unit', 'city', 'region', 'postcode', 'latitude', 'longitude']
    with open(OUT_RAW, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(addresses)

    residential = [a for a in addresses if not is_commercial(a)]
    with open(OUT_FMT, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['address'])
        for a in residential:
            unit_part = f' {a["unit"]}' if a['unit'] else ''
            city = a['city'].title() or CITY_DEFAULT
            w.writerow([f'{a["number"]} {a["street"]}{unit_part}, {city}, OH, {ZIP}'])

    cities = Counter(a['city'] for a in addresses)
    print(f'GeoJSON features scanned: {scanned}')
    print(f'Unique 43232 addresses:   {len(addresses)} -> {OUT_RAW}')
    print(f'Formatted (keyword commercial filter): {len(residential)} -> {OUT_FMT}')
    print('City breakdown:', dict(cities.most_common(8)))


if __name__ == '__main__':
    main()
