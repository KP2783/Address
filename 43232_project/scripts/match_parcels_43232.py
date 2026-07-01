#!/usr/bin/env python3
"""Match 43232 addresses to Franklin County auditor parcel data (FULL county file).

IMPORTANT: we match against the FULL shared/data/franklin_county_parcels.csv by
normalized address key, NOT a ZIPCODE-filtered subset. The auditor ZIPCODE field
is unreliable (a road crossing ZIP boundaries is coded to a neighboring zip),
and filtering parcels to ZIP==43232 dropped ~half the valid matches. Matching is
by (number + street), so the full file gives full coverage; only 43232 addresses
are read from the GeoJSON side.

Stores only the fields needed for classification (slim records) to bound memory.
"""
import csv
import os
import re

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, '..', 'data')
ZIP = '43232'

ADDRESSES_FILE = os.path.join(DATA_DIR, f'addresses_{ZIP}.csv')
PARCELS_FILE = '/Users/kevinpatel/Address/shared/data/franklin_county_parcels.csv'
OUTPUT_FILE = os.path.join(DATA_DIR, f'addresses_{ZIP}_enriched.csv')

RESIDENTIAL_LAND_USE = {
    '500', '501', '503',                          # residential vacant land
    '510', '511',                                 # single family
    '520', '530',                                 # two/three family
    '550', '551', '552', '553', '559', '560',     # apartments
}

# Only these parcel fields are needed downstream — store these (slim records).
KEEP = ['PARCEL ID', 'STADDR', 'STHNUM', 'STDIRE', 'STNAME', 'STSFX',
        'LANDUSE', 'HOMSTD', 'OWNER_ADD1', 'NAME1', 'YEARBLT',
        'BEDRMS', 'BATHS', 'HBATHS', 'ROOMS', 'APPRTOT', 'ANN_TAX',
        'PRICE', 'TRANDT']


def normalize_addr(addr_str):
    s = re.sub(r'\s+', ' ', (addr_str or '').upper()).strip()
    s = re.sub(r'\s+(APT|UNIT|STE|SUITE|#)\s*\S*$', '', s)
    s = re.sub(r'^(\d+)\s*-\s*\d+\s+', r'\1 ', s)   # leading number range -> first number
    s = re.sub(r'-', ' ', s)                          # hyphens in names (NOE-BIXBY -> NOE BIXBY)
    s = re.sub(r'\s+', ' ', s).strip()
    for old, new in {' BL': ' BLVD', ' BOULEVARD': ' BLVD', ' AVENUE': ' AVE',
                     ' DRIVE': ' DR', ' STREET': ' ST', ' ROAD': ' RD',
                     ' COURT': ' CT', ' LANE': ' LN', ' PLACE': ' PL',
                     ' CIRCLE': ' CIR', ' PIKE': ' PK', ' TERRACE': ' TER',
                     ' PARKWAY': ' PKWY', ' HIGHWAY': ' HWY', ' TRACE': ' TRCE',
                     ' TRAIL': ' TRL', ' COVE': ' CV', ' POINT': ' PT'}.items():
        if s.endswith(old):
            s = s[:-len(old)] + new
    s = re.sub(r'\s+[NSEW]$', '', s)                 # trailing directional suffix
    return s


def slim(row):
    return {f: (row.get(f, '') or '').strip() for f in KEEP}


def classify_occupancy(p):
    if p.get('HOMSTD', '') == 'Y':
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
    m = {
        '500': 'RESIDENTIAL_VACANT', '501': 'RESIDENTIAL_VACANT', '503': 'RESIDENTIAL_VACANT',
        '510': 'SINGLE_FAMILY', '511': 'SINGLE_FAMILY',
        '520': 'TWO_FAMILY', '530': 'THREE_FAMILY',
        '550': 'APARTMENT_4PLUS', '551': 'APARTMENT', '552': 'APARTMENT',
        '553': 'APARTMENT', '559': 'APARTMENT', '560': 'APARTMENT',
    }
    if code in m:
        return m[code]
    if code.startswith('3'):
        return 'INDUSTRIAL'
    if code.startswith('4'):
        return 'COMMERCIAL'
    if code[0:1] in ('6', '7', '8'):
        return 'EXEMPT'
    return 'OTHER'


def main():
    parcel_lookup = {}
    street_lookup = {}
    parcels_loaded = 0
    with open(PARCELS_FILE, newline='', encoding='utf-8-sig') as f:
        for row in csv.DictReader(f):
            s = slim(row)
            if not s['STHNUM']:
                continue
            parcels_loaded += 1
            key = normalize_addr(s['STADDR'])
            parcel_lookup.setdefault(key, s)
            rng = re.match(r'^(\d+)\s*-\s*(\d+)\s+(.+)', s['STADDR'])
            if rng:
                n1, n2, part = rng.groups()
                for nk in (n1, n2):
                    parcel_lookup.setdefault(normalize_addr(f'{nk} {part}'), s)
                try:
                    lo, hi = int(n1), int(n2)
                    if hi - lo <= 20:  # guard against absurd ranges
                        for n in range(lo, hi + 1):
                            parcel_lookup.setdefault(normalize_addr(f'{n} {part}'), s)
                except ValueError:
                    pass
            sk = normalize_addr(f"{s['STHNUM']} {s['STDIRE']} {s['STNAME']} {s['STSFX']}".strip())
            street_lookup.setdefault(sk, s)
    print(f'Loaded {parcels_loaded} parcels | lookup keys: {len(parcel_lookup)} | street keys: {len(street_lookup)}')

    output_fields = [
        'number', 'street', 'unit', 'city', 'region', 'postcode',
        'latitude', 'longitude',
        'parcel_id', 'land_use_code', 'land_use_type', 'occupancy',
        'owner_name', 'homestead', 'year_built', 'bedrooms', 'bathrooms',
        'half_baths', 'rooms', 'appraised_value', 'annual_tax',
        'sale_price', 'sale_date', 'match_status',
    ]

    matched = unmatched = residential = commercial = owner_occ = rental = 0
    with open(ADDRESSES_FILE, newline='') as fin, \
         open(OUTPUT_FILE, 'w', newline='') as fout:
        reader = csv.DictReader(fin)
        writer = csv.DictWriter(fout, fieldnames=output_fields)
        writer.writeheader()
        for row in reader:
            number = (row['number'] or '').strip()
            street = re.sub(r'\s+', ' ', (row['street'] or '')).strip()
            addr_key = normalize_addr(f'{number} {street}')
            out = {
                'number': number, 'street': street,
                'unit': row.get('unit', ''), 'city': row.get('city', ''),
                'region': 'OH', 'postcode': ZIP,
                'latitude': row.get('latitude', ''), 'longitude': row.get('longitude', ''),
            }
            p = parcel_lookup.get(addr_key)
            if not p and (row.get('unit') or ''):
                p = street_lookup.get(addr_key)
            if not p:
                for prefix in ['S ', 'N ', 'E ', 'W ']:
                    k = normalize_addr(f'{number} {prefix}{street}')
                    p = parcel_lookup.get(k) or street_lookup.get(k)
                    if p:
                        break
            if not p:
                stripped = re.sub(r'^([SNEW])\s+', '', street)
                if stripped != street:
                    k = normalize_addr(f'{number} {stripped}')
                    p = parcel_lookup.get(k) or street_lookup.get(k)

            if p:
                matched += 1
                lu = p.get('LANDUSE', '')
                occ = classify_occupancy(p)
                if lu in RESIDENTIAL_LAND_USE:
                    residential += 1
                else:
                    commercial += 1
                if occ in ('OWNER_OCCUPIED', 'LIKELY_OWNER'):
                    owner_occ += 1
                elif occ == 'LIKELY_RENTAL':
                    rental += 1
                out.update({
                    'parcel_id': p.get('PARCEL ID', ''), 'land_use_code': lu,
                    'land_use_type': classify_land_use(lu), 'occupancy': occ,
                    'owner_name': p.get('NAME1', ''), 'homestead': p.get('HOMSTD', ''),
                    'year_built': p.get('YEARBLT', ''), 'bedrooms': p.get('BEDRMS', ''),
                    'bathrooms': p.get('BATHS', ''), 'half_baths': p.get('HBATHS', ''),
                    'rooms': p.get('ROOMS', ''), 'appraised_value': p.get('APPRTOT', ''),
                    'annual_tax': p.get('ANN_TAX', ''), 'sale_price': p.get('PRICE', ''),
                    'sale_date': p.get('TRANDT', ''), 'match_status': 'MATCHED',
                })
            else:
                unmatched += 1
                out.update({k: '' for k in output_fields if k not in out})
                out['match_status'] = 'UNMATCHED'
            writer.writerow(out)

    total = matched + unmatched
    print(f'\nTotal addresses: {total}')
    print(f'Matched to parcels: {matched} ({matched/total*100:.1f}%)')
    print(f'Unmatched: {unmatched} ({unmatched/total*100:.1f}%)')
    print(f'Of matched -> residential: {residential} | commercial/other: {commercial}')
    print(f'Owner-occupied: {owner_occ} | likely rental: {rental}')
    print(f'Output: {OUTPUT_FILE}')


if __name__ == '__main__':
    main()
