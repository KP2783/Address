#!/usr/bin/env python3
"""Reformat the 43232 accurate list into the SAME schema as the other ZIPs.

Matches 43213_project/data/addresses_43213_residential_final.csv exactly:
  address,number,street,unit,city,state,zip,latitude,longitude,
  final_classification,classification_source,google_validated_address,google_city,
  parcel_id,land_use_code,land_use_type,occupancy,owner_name,homestead,
  year_built,bedrooms,bathrooms,appraised_value,annual_tax,sale_price,sale_date

Sources:
  Tier A (parcel address-match + Census) <- addresses_43232_clean_validated.csv
  Tier D (spatial nearest-parcel + Census) <- validated_residential_43232.csv
Both joined to the full parcel record by parcel_id for owner/homestead/structure fields.

Output: addresses_43232_residential_final.csv  (matches the 43213 filename + schema)
"""
import csv
import os
import re

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, '..', 'data')
ZIP = '43232'
PARCELS_FULL = '/Users/kevinpatel/Address/shared/data/franklin_county_parcels.csv'

CLEAN_VALIDATED = os.path.join(DATA_DIR, f'addresses_{ZIP}_clean_validated.csv')   # Tier A
SPATIAL = os.path.join(DATA_DIR, f'validated_residential_{ZIP}.csv')               # Tier D
RECOVERED = os.path.join(DATA_DIR, f'recovered_{ZIP}.csv')                         # Census-confirmed
UNRECOVERABLE = os.path.join(DATA_DIR, f'unrecoverable_{ZIP}.csv')                 # Census match/no-match
OUT = os.path.join(DATA_DIR, f'addresses_{ZIP}_residential_final.csv')

FIELDS = ['address', 'number', 'street', 'unit', 'city', 'state', 'zip',
          'latitude', 'longitude', 'final_classification', 'classification_source',
          'google_validated_address', 'google_city',
          'parcel_id', 'land_use_code', 'land_use_type', 'occupancy', 'owner_name',
          'homestead', 'year_built', 'bedrooms', 'bathrooms',
          'appraised_value', 'annual_tax', 'sale_price', 'sale_date']


def classify_occupancy(p):
    if (p.get('HOMSTD', '') or '').strip() == 'Y':
        return 'OWNER_OCCUPIED'
    owner = re.sub(r'\s+', ' ', (p.get('OWNER_ADD1', '') or '').upper()).strip()
    prop = re.sub(r'\s+', ' ', (p.get('STADDR', '') or '').upper()).strip()
    if owner and prop:
        if prop in owner:
            return 'LIKELY_OWNER'
        if owner != prop:
            return 'LIKELY_RENTAL'
    return 'UNKNOWN'


def classify_land_use(code):
    m = {'500': 'RESIDENTIAL_VACANT', '501': 'RESIDENTIAL_VACANT', '503': 'RESIDENTIAL_VACANT',
         '510': 'SINGLE_FAMILY', '511': 'SINGLE_FAMILY', '520': 'TWO_FAMILY', '530': 'THREE_FAMILY',
         '550': 'APARTMENT_4PLUS', '551': 'APARTMENT', '552': 'APARTMENT', '553': 'APARTMENT',
         '559': 'APARTMENT', '560': 'APARTMENT'}
    if code in m:
        return m[code]
    if code.startswith('3'):
        return 'INDUSTRIAL'
    if code.startswith('4'):
        return 'COMMERCIAL'
    if code[:1] in ('6', '7', '8'):
        return 'EXEMPT'
    return 'OTHER'


def load_parcels():
    p = {}
    with open(PARCELS_FULL, newline='', encoding='utf-8-sig') as f:
        for row in csv.DictReader(f):
            pid = (row.get('PARCEL ID', '') or '').strip()
            if pid:
                p[pid] = row
    return p


def load_census_confirmed():
    """Set of number|STREET|UNIT that Census confirmed as real (from recovery run)."""
    conf = set()
    for r in csv.DictReader(open(RECOVERED, newline='')):
        conf.add(f"{r['number'].strip()}|{r['street'].strip().upper()}|{(r.get('unit') or '').strip().upper()}")
    for r in csv.DictReader(open(UNRECOVERABLE, newline='')):
        if r.get('census_status') == 'Match':
            conf.add(f"{r['number'].strip()}|{r['street'].strip().upper()}|{(r.get('unit') or '').strip().upper()}")
    return conf


def main():
    parcels = load_parcels()
    n_a = n_d = 0
    with open(OUT, 'w', newline='') as fout:
        w = csv.DictWriter(fout, fieldnames=FIELDS)
        w.writeheader()

        def write_row(r, source):
            nonlocal n_a, n_d
            parcel = parcels.get((r.get('parcel_id') or '').strip(), {})
            unit = (r.get('unit') or '').strip()
            up = f' {unit}' if unit else ''
            city = r.get('city', '').strip() or 'Columbus'
            w.writerow({
                'address': f"{r['number']} {r['street']}{up}, {city.upper()}, OH, {ZIP}",
                'number': r['number'], 'street': r['street'], 'unit': unit,
                'city': city.title(), 'state': 'OH', 'zip': ZIP,
                'latitude': r.get('latitude', ''), 'longitude': r.get('longitude', ''),
                'final_classification': 'RESIDENTIAL',
                'classification_source': source,
                'google_validated_address': '',     # no Google used (free/parcel-only run)
                'google_city': '',
                'parcel_id': r.get('parcel_id', ''),
                'land_use_code': parcel.get('LANDUSE', ''),
                'land_use_type': classify_land_use(parcel.get('LANDUSE', '')),
                'occupancy': classify_occupancy(parcel),
                'owner_name': parcel.get('NAME1', ''),
                'homestead': parcel.get('HOMSTD', ''),
                'year_built': parcel.get('YEARBLT', ''),
                'bedrooms': parcel.get('BEDRMS', ''),
                'bathrooms': parcel.get('BATHS', ''),
                'appraised_value': parcel.get('APPRTOT', ''),
                'annual_tax': parcel.get('ANN_TAX', ''),
                'sale_price': parcel.get('PRICE', ''),
                'sale_date': parcel.get('TRANDT', ''),
            })
            if source.startswith('auditor_parcel_addr'):
                n_a += 1
            else:
                n_d += 1

        for r in csv.DictReader(open(CLEAN_VALIDATED, newline='')):
            write_row(r, 'auditor_parcel_address_match')
        census_confirmed = load_census_confirmed()
        skipped = 0
        for r in csv.DictReader(open(SPATIAL, newline='')):
            k = f"{r['number'].strip()}|{r['street'].strip().upper()}|{(r.get('unit') or '').strip().upper()}"
            if k not in census_confirmed:        # Tier D requires BOTH spatial-residential AND Census-real
                skipped += 1
                continue
            write_row(r, 'auditor_parcel_spatial_match')
        print(f'  Tier D skipped (spatial-residential but Census-unconfirmed): {skipped}')

    print(f'Wrote {OUT}')
    print(f'  Tier A (parcel address-match + Census): {n_a}')
    print(f'  Tier D (spatial nearest-parcel + Census): {n_d}')
    print(f'  TOTAL: {n_a + n_d}  (schema matches 43213 residential_final)')


if __name__ == '__main__':
    main()
