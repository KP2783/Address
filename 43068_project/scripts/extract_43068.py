#!/usr/bin/env python3
"""Extract 43068 addresses from Ohio GeoJSON data (Franklin, Licking, Fairfield counties)."""

import csv
import json
import re
from collections import Counter

COUNTY_FILES = [
    'franklin-addresses-county.geojson',
    'licking-addresses-county.geojson',
    'licking2-addresses-county.geojson',
    'fairfield-addresses-county.geojson',
    'city_of_columbus-addresses-city.geojson',
]
OUTPUT_RAW = '/Users/kevinpatel/Address/43068_project/data/addresses_43068.csv'
OUTPUT_FMT = '/Users/kevinpatel/Address/43068_project/data/addresses_43068_formatted.csv'

# Commercial indicators to filter out
COMMERCIAL_UNITS = ['STE', 'SUITE', 'FLOOR', 'FL', 'LOBBY', 'OFFICE', 'OFC', 'BLDG', 'DEPT']
COMMERCIAL_STREETS = ['PLAZA', 'MALL', 'INDUSTRIAL', 'COMMERCE', 'CORPORATE']


def is_commercial(row):
    unit = row.get('unit', '').upper()
    street = row.get('street', '').upper()

    for indicator in COMMERCIAL_UNITS:
        if indicator in unit:
            return True

    for indicator in COMMERCIAL_STREETS:
        if indicator in street:
            return True

    return False


def normalize_street(s):
    return re.sub(r'\s+', ' ', s).strip()


def main():
    addresses = []
    seen = set()

    for county_file in COUNTY_FILES:
        filepath = f'/Users/kevinpatel/Address/oh/{county_file}'
        count = 0
        try:
            with open(filepath, 'r') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        feat = json.loads(line)
                        props = feat.get('properties', {})
                        postcode = props.get('postcode', '')
                        if postcode != '43068':
                            continue

                        number = (props.get('number') or '').strip()
                        street = normalize_street(props.get('street') or '')
                        if not number or not street:
                            continue

                        unit = (props.get('unit') or '').strip()
                        city = (props.get('city') or '').strip()
                        region = (props.get('region') or 'OH').strip()

                        coords = feat.get('geometry', {}).get('coordinates', [0, 0])
                        lon, lat = coords[0], coords[1]

                        # Dedup key
                        key = f'{number}|{street}|{unit}'
                        if key in seen:
                            continue
                        seen.add(key)

                        row = {
                            'number': number,
                            'street': street,
                            'unit': unit,
                            'city': city,
                            'region': region,
                            'postcode': '43068',
                            'latitude': lat,
                            'longitude': lon,
                        }

                        addresses.append(row)
                        count += 1
                    except json.JSONDecodeError:
                        continue
        except FileNotFoundError:
            print(f'File not found: {filepath}')
            continue
        print(f'{county_file}: {count} addresses for 43068')

    print(f'\nTotal unique: {len(addresses)}')

    # City breakdown
    cities = Counter(a['city'] for a in addresses)
    print('\nCity breakdown:')
    for c, n in cities.most_common():
        print(f'  {c}: {n}')

    # Write raw CSV
    fields = ['number', 'street', 'unit', 'city', 'region', 'postcode', 'latitude', 'longitude']
    with open(OUTPUT_RAW, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(addresses)
    print(f'\nRaw file: {OUTPUT_RAW}')

    # Filter residential and write formatted
    residential = [a for a in addresses if not is_commercial(a)]
    print(f'\nAfter commercial filter: {len(residential)} (removed {len(addresses) - len(residential)} commercial)')

    # Fix township names to proper USPS cities
    CITY_FIXES = {
        'ETNA TWP': 'Pataskala',
        'TRURO TWP': 'Reynoldsburg',
        'JEFFERSON TWP': 'Reynoldsburg',
        'VIOLET TWP': 'Pickerington',
        '': 'Reynoldsburg',
    }

    with open(OUTPUT_FMT, 'w') as f:
        f.write('address\n')
        for a in residential:
            street = a['street']
            unit_part = f' {a["unit"]}' if a['unit'] else ''
            city_raw = a['city'].upper().strip()
            city = CITY_FIXES.get(city_raw, a['city'].title())
            line = f'{a["number"]} {street}{unit_part}, {city}, OH, 43068'
            f.write(line + '\n')
    print(f'Formatted file: {OUTPUT_FMT}')
    print(f'Total residential addresses: {len(residential)}')


if __name__ == '__main__':
    main()
