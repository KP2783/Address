#!/usr/bin/env python3
"""
Match 43068 addresses to Franklin County auditor parcel data.
Produces a merged CSV with residential classification, owner-occupied vs rental,
year built, beds/baths, appraised value, etc.
"""

import csv
import re

ADDRESSES_FILE = '/Users/kevinpatel/Address/43068_project/data/addresses_43068.csv'
PARCELS_FILE = '/Users/kevinpatel/Address/43068_project/data/parcels_43068.csv'
OUTPUT_FILE = '/Users/kevinpatel/Address/43068_project/data/addresses_43068_enriched.csv'

# Residential land use codes
RESIDENTIAL_LAND_USE = {
    '500', '501', '503',       # residential vacant land
    '510', '511',              # single family
    '520', '530',              # two-family, three-family
    '550', '551', '552', '553', '559', '560',  # apartments
}

# Apartment complexes on commercial parcels
APT_COMPLEX_LAND_USE = {'401'}


def normalize_addr(addr_str):
    s = addr_str.upper().strip()
    s = re.sub(r'\s+', ' ', s)
    s = re.sub(r'\s+(APT|UNIT|STE|SUITE|#)\s*\S*$', '', s)
    s = re.sub(r'^(\d+)\s*-\s*\d+\s+', r'\1 ', s)
    replacements = {
        ' BL': ' BLVD', ' BOULEVARD': ' BLVD',
        ' AVENUE': ' AVE', ' DRIVE': ' DR',
        ' STREET': ' ST', ' ROAD': ' RD',
        ' COURT': ' CT', ' LANE': ' LN',
        ' PLACE': ' PL', ' CIRCLE': ' CIR',
    }
    for old, new in replacements.items():
        if s.endswith(old):
            s = s[:-len(old)] + new
    return s


def classify_occupancy(parcel):
    homstd = parcel.get('HOMSTD', '').strip()
    if homstd == 'Y':
        return 'OWNER_OCCUPIED'
    owner_addr = parcel.get('OWNER_ADD1', '').upper().strip()
    prop_addr = parcel.get('STADDR', '').upper().strip()
    if owner_addr and prop_addr:
        owner_norm = re.sub(r'\s+', ' ', owner_addr).strip()
        prop_norm = re.sub(r'\s+', ' ', prop_addr).strip()
        if prop_norm and prop_norm in owner_norm:
            return 'LIKELY_OWNER'
    if owner_addr and prop_addr and owner_addr != prop_addr:
        return 'LIKELY_RENTAL'
    return 'UNKNOWN'


def classify_land_use(code):
    land_use_map = {
        '500': 'RESIDENTIAL_VACANT', '501': 'RESIDENTIAL_VACANT', '503': 'RESIDENTIAL_VACANT',
        '510': 'SINGLE_FAMILY', '511': 'SINGLE_FAMILY',
        '520': 'TWO_FAMILY', '530': 'THREE_FAMILY',
        '550': 'APARTMENT_4PLUS', '551': 'APARTMENT', '552': 'APARTMENT',
        '553': 'APARTMENT', '559': 'APARTMENT', '560': 'APARTMENT',
    }
    if code in land_use_map:
        return land_use_map[code]
    if code.startswith('3'):
        return 'INDUSTRIAL'
    if code.startswith('4'):
        return 'COMMERCIAL'
    if code.startswith('6') or code.startswith('7') or code.startswith('8'):
        return 'EXEMPT'
    return 'OTHER'


def main():
    print("Loading parcel data...")
    parcel_lookup = {}
    street_lookup = {}

    with open(PARCELS_FILE, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            sthnum = row.get('STHNUM', '').strip()
            staddr = row.get('STADDR', '').strip()
            stdire = row.get('STDIRE', '').strip()
            stname = row.get('STNAME', '').strip()
            stsfx = row.get('STSFX', '').strip()

            if not sthnum:
                continue

            key = normalize_addr(staddr)
            if key not in parcel_lookup:
                parcel_lookup[key] = row

            # Handle address ranges
            range_match = re.match(r'^(\d+)\s*-\s*(\d+)\s+(.+)', staddr)
            if range_match:
                num1, num2, street_part = range_match.groups()
                key1 = normalize_addr(f"{num1} {street_part}")
                key2 = normalize_addr(f"{num2} {street_part}")
                if key1 not in parcel_lookup:
                    parcel_lookup[key1] = row
                if key2 not in parcel_lookup:
                    parcel_lookup[key2] = row
                try:
                    n1, n2 = int(num1), int(num2)
                    for n in range(n1, n2 + 1):
                        between_key = normalize_addr(f"{n} {street_part}")
                        if between_key not in parcel_lookup:
                            parcel_lookup[between_key] = row
                except ValueError:
                    pass

            street_key = normalize_addr(f"{sthnum} {stdire} {stname} {stsfx}".strip())
            if street_key not in street_lookup:
                street_lookup[street_key] = row

    print(f"Loaded {len(parcel_lookup)} parcel lookup keys, {len(street_lookup)} street keys")

    print("Matching addresses to parcels...")
    output_fields = [
        'number', 'street', 'unit', 'city', 'region', 'postcode',
        'latitude', 'longitude',
        'parcel_id', 'land_use_code', 'land_use_type', 'occupancy',
        'owner_name', 'homestead', 'year_built', 'bedrooms', 'bathrooms',
        'half_baths', 'rooms', 'air_conditioning', 'appraised_value',
        'annual_tax', 'sale_price', 'sale_date',
        'match_status'
    ]

    matched = 0
    unmatched = 0
    residential = 0
    commercial = 0
    owner_occ = 0
    rental = 0

    with open(ADDRESSES_FILE, 'r') as fin, open(OUTPUT_FILE, 'w', newline='') as fout:
        reader = csv.DictReader(fin)
        writer = csv.DictWriter(fout, fieldnames=output_fields)
        writer.writeheader()

        for row in reader:
            number = row['number'].strip()
            street = re.sub(r'\s+', ' ', row['street']).strip()
            addr_key = normalize_addr(f"{number} {street}")

            out = {
                'number': number,
                'street': street,
                'unit': row.get('unit', ''),
                'city': row.get('city', ''),
                'region': 'OH',
                'postcode': '43068',
                'latitude': row.get('latitude', ''),
                'longitude': row.get('longitude', ''),
            }

            parcel = parcel_lookup.get(addr_key)

            if not parcel and row.get('unit', ''):
                parcel = street_lookup.get(addr_key)

            if not parcel:
                for prefix in ['S ', 'N ', 'E ', 'W ']:
                    alt_key = normalize_addr(f"{number} {prefix}{street}")
                    parcel = parcel_lookup.get(alt_key) or street_lookup.get(alt_key)
                    if parcel:
                        break

            if not parcel:
                stripped = re.sub(r'^([SNEW])\s+', '', street)
                if stripped != street:
                    alt_key = normalize_addr(f"{number} {stripped}")
                    parcel = parcel_lookup.get(alt_key) or street_lookup.get(alt_key)

            if parcel:
                matched += 1
                lu = parcel.get('LANDUSE', '')
                lu_type = classify_land_use(lu)
                occ = classify_occupancy(parcel)

                if lu in RESIDENTIAL_LAND_USE or lu in APT_COMPLEX_LAND_USE:
                    residential += 1
                else:
                    commercial += 1

                if occ in ('OWNER_OCCUPIED', 'LIKELY_OWNER'):
                    owner_occ += 1
                elif occ == 'LIKELY_RENTAL':
                    rental += 1

                out.update({
                    'parcel_id': parcel.get('PARCEL ID', ''),
                    'land_use_code': lu,
                    'land_use_type': lu_type,
                    'occupancy': occ,
                    'owner_name': parcel.get('NAME1', ''),
                    'homestead': parcel.get('HOMSTD', ''),
                    'year_built': parcel.get('YEARBLT', ''),
                    'bedrooms': parcel.get('BEDRMS', ''),
                    'bathrooms': parcel.get('BATHS', ''),
                    'half_baths': parcel.get('HBATHS', ''),
                    'rooms': parcel.get('ROOMS', ''),
                    'air_conditioning': parcel.get('AIRCOND', ''),
                    'appraised_value': parcel.get('APPRTOT', ''),
                    'annual_tax': parcel.get('ANN_TAX', ''),
                    'sale_price': parcel.get('PRICE', ''),
                    'sale_date': parcel.get('TRANDT', ''),
                    'match_status': 'MATCHED',
                })
            else:
                unmatched += 1
                out.update({k: '' for k in output_fields if k not in out})
                out['match_status'] = 'UNMATCHED'

            writer.writerow(out)

    total = matched + unmatched
    print(f"\n=== Results ===")
    print(f"Total addresses: {total}")
    print(f"Matched to parcels: {matched} ({matched/total*100:.1f}%)")
    print(f"Unmatched: {unmatched}")
    print(f"\nOf matched:")
    print(f"  Residential: {residential}")
    print(f"  Commercial/Other: {commercial}")
    print(f"  Owner-occupied: {owner_occ}")
    print(f"  Likely rental: {rental}")
    print(f"\nOutput: {OUTPUT_FILE}")


if __name__ == '__main__':
    main()
