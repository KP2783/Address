#!/usr/bin/env python3
"""Finalize 43232: produce the residential deliverable (parcel-only, no paid API).

Two confidence tiers:
  - TIER 1 (high): matched to a parcel whose LANDUSE is a residential DWELLING.
        Occupancy labeled OCCUPIED/UNKNOWN from homestead + owner-vs-property address.
  - TIER 2 (inferred): UNMATCHED addresses whose street is residential per the
        auditor parcel file (>=70% dwelling land-use among parcels on that street,
        >=3 parcels). These are mostly condo/apartment complexes whose GeoJSON
        unit-numbering can't be matched to parcel street-numbers, but the street
        itself is residential. Occupancy = UNKNOWN.

Excluded: commercial/industrial/exempt, residential-vacant-land, and unmatched
addresses on non-residential or unclassified streets (written to review/ for
auditor spot-check).
"""
import csv
import os
import re

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, '..', 'data')
REVIEW_DIR = os.path.join(SCRIPT_DIR, '..', 'data')  # review sits under data/ for now
ZIP = '43232'

ENRICHED = os.path.join(DATA_DIR, f'addresses_{ZIP}_enriched.csv')
PARCELS_FULL = '/Users/kevinpatel/Address/shared/data/franklin_county_parcels.csv'
FINAL = os.path.join(DATA_DIR, f'addresses_{ZIP}_residential_final.csv')
REVIEW = os.path.join(DATA_DIR, f'unverified_{ZIP}.csv')

DWELLING = {'510', '511', '520', '530', '550', '551', '552', '553', '559', '560'}
VACANT_LAND = {'500', '501', '503'}
OCCUPIED_TYPES = {'OWNER_OCCUPIED', 'LIKELY_OWNER', 'LIKELY_RENTAL'}
STREET_THRESHOLD = 0.70      # dwelling fraction to call a street residential
STREET_MIN_PARCELS = 3

FINAL_FIELDS = [
    'address', 'number', 'street', 'unit', 'city', 'state', 'zip',
    'latitude', 'longitude',
    'final_classification', 'classification_source', 'confidence',
    'occupancy', 'occupancy_label',
    'parcel_id', 'land_use_code', 'land_use_type',
    'owner_name', 'homestead', 'year_built', 'bedrooms', 'bathrooms',
    'appraised_value', 'annual_tax', 'sale_price', 'sale_date',
]
REVIEW_FIELDS = ['number', 'street', 'unit', 'city', 'postcode', 'latitude', 'longitude', 'reason']


def street_key(name, sfx=''):
    """Canonical street name so address-side and parcel-side streets align."""
    s = f'{name} {sfx}'.upper().strip()
    s = re.sub(r'-', ' ', s)
    s = re.sub(r'\s+', ' ', s).strip()
    full = {'WY': 'WAY', 'PL': 'PLACE', 'CT': 'COURT', 'LN': 'LANE', 'DR': 'DRIVE',
            'RD': 'ROAD', 'ST': 'STREET', 'AVE': 'AVENUE', 'CIR': 'CIRCLE',
            'BLVD': 'BOULEVARD', 'PK': 'PIKE', 'TER': 'TERRACE', 'PKWY': 'PARKWAY',
            'HWY': 'HIGHWAY', 'TRL': 'TRAIL', 'CV': 'COVE', 'PT': 'POINT'}
    for ab, ful in full.items():
        s = re.sub(r'\b' + ab + r'$', ful, s)
    s = re.sub(r'\s+[NSEW]$', '', s)          # drop trailing directional
    s = re.sub(r'^([SNEW])\s+', '', s)         # drop leading directional
    return s


def build_street_signal():
    """street_key -> (dwelling_count, total_count) from the full parcel file."""
    sig = {}
    with open(PARCELS_FULL, newline='', encoding='utf-8-sig') as f:
        for row in csv.DictReader(f):
            stname = (row.get('STNAME', '') or '').strip()
            if not stname:
                continue
            key = street_key(stname, row.get('STSFX', ''))
            lu = (row.get('LANDUSE', '') or '').strip()
            d, t = sig.get(key, (0, 0))
            sig[key] = (d + (1 if lu in DWELLING else 0), t + 1)
    return sig


def main():
    os.makedirs(DATA_DIR, exist_ok=True)
    print('Building street residential signal from parcel file...')
    street_sig = build_street_signal()
    print(f'  streets: {len(street_sig)}')

    counts = {'tier1_matched': 0, 'tier2_inferred': 0, 'vacant_land': 0,
              'commercial_other': 0, 'unverified': 0}
    occ_counts = {'OCCUPIED': 0, 'UNKNOWN': 0, 'VACANT': 0}

    with open(ENRICHED, newline='') as fin, \
         open(FINAL, 'w', newline='') as ffout, \
         open(REVIEW, 'w', newline='') as rfout:
        reader = csv.DictReader(fin)
        fw = csv.DictWriter(ffout, fieldnames=FINAL_FIELDS)
        fw.writeheader()
        rw = csv.DictWriter(rfout, fieldnames=REVIEW_FIELDS)
        rw.writeheader()

        for r in reader:
            lu = (r.get('land_use_code') or '').strip()
            occ = (r.get('occupancy') or '').strip()
            matched = r.get('match_status') == 'MATCHED'
            number = r['number']
            street = r['street']
            unit = (r.get('unit') or '').strip()
            city = (r.get('city') or '').strip().title() or 'Columbus'

            def emit(source, confidence, occ_label, base=None):
                counts['tier1_matched' if source == 'parcel_land_use' else 'tier2_inferred'] += 1
                occ_counts[occ_label] = occ_counts.get(occ_label, 0) + 1
                up = f' {unit}' if unit else ''
                fw.writerow({
                    'address': f'{number} {street}{up}, {city}, OH, {ZIP}',
                    'number': number, 'street': street, 'unit': unit,
                    'city': city, 'state': 'OH', 'zip': ZIP,
                    'latitude': r.get('latitude', ''), 'longitude': r.get('longitude', ''),
                    'final_classification': 'RESIDENTIAL',
                    'classification_source': source, 'confidence': confidence,
                    'occupancy': occ if source == 'parcel_land_use' else '',
                    'occupancy_label': occ_label,
                    'parcel_id': r.get('parcel_id', ''), 'land_use_code': lu,
                    'land_use_type': r.get('land_use_type', ''),
                    'owner_name': r.get('owner_name', ''), 'homestead': r.get('homestead', ''),
                    'year_built': r.get('year_built', ''), 'bedrooms': r.get('bedrooms', ''),
                    'bathrooms': r.get('bathrooms', ''),
                    'appraised_value': r.get('appraised_value', ''), 'annual_tax': r.get('annual_tax', ''),
                    'sale_price': r.get('sale_price', ''), 'sale_date': r.get('sale_date', ''),
                })

            if matched and lu in DWELLING:
                label = 'OCCUPIED' if occ in OCCUPIED_TYPES else 'UNKNOWN'
                emit('parcel_land_use', 'HIGH', label)
            elif matched and lu in VACANT_LAND:
                counts['vacant_land'] += 1
            elif matched:
                counts['commercial_other'] += 1
                rw.writerow({**{k: r.get(k, '') for k in REVIEW_FIELDS},
                             'reason': f'matched {r.get("land_use_type","")}'})
            else:
                # unmatched: try street-level residential inference
                key = street_key(street)
                dwell, tot = street_sig.get(key, (0, 0))
                if tot >= STREET_MIN_PARCELS and dwell / tot >= STREET_THRESHOLD:
                    emit('street_inference', 'MEDIUM', 'UNKNOWN')
                else:
                    counts['unverified'] += 1
                    reason = f'no parcel; street parcels={tot} dwelling={dwell}'
                    rw.writerow({**{k: r.get(k, '') for k in REVIEW_FIELDS}, 'reason': reason})

    total = sum(counts.values())
    print('\n=== 43232 final breakdown ===')
    for k, v in counts.items():
        print(f'  {k:18}: {v:6} ({v/total*100:.1f}%)')
    print(f'  {"TOTAL":18}: {total}')
    residential = counts['tier1_matched'] + counts['tier2_inferred']
    print(f'\nResidential in deliverable: {residential} '
          f'(Tier1 high-conf: {counts["tier1_matched"]}, Tier2 inferred: {counts["tier2_inferred"]})')
    print('Occupancy labels:', occ_counts)
    print(f'\nDeliverable : {FINAL}')
    print(f'Unverified  : {REVIEW}')


if __name__ == '__main__':
    main()
