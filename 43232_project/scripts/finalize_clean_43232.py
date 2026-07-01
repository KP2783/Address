#!/usr/bin/env python3
"""Finalize 43232 — CLEAN, no-guess residential list.

Keeps ONLY addresses that are auditor-verified residential dwellings (matched to
a parcel whose LANDUSE is a dwelling code). Drops every inferred/heuristic field:
  - street-inferred rows (Tier 2)            -> excluded
  - occupancy classification (LIKELY_OWNER / LIKELY_RENTAL / OCCUPIED) -> dropped (heuristics)
Only recorded facts remain: parcel_id, land_use, homestead (raw HOMSTD), year
built, beds, baths, appraised value, etc.

City normalized to Columbus (USPS-acceptable city for 43232; the GeoJSON
township names like 'Madison Twp' are a common return cause).

Output: addresses_43232_clean.csv  (input to the Census legitimacy check).
"""
import csv
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, '..', 'data')
ZIP = '43232'
CITY = 'Columbus'

ENRICHED = os.path.join(DATA_DIR, f'addresses_{ZIP}_enriched.csv')
OUT = os.path.join(DATA_DIR, f'addresses_{ZIP}_clean.csv')

DWELLING = {'510', '511', '520', '530', '550', '551', '552', '553', '559', '560'}

# Factual fields only — no heuristics, no inferred labels.
FIELDS = [
    'address', 'number', 'street', 'unit', 'city', 'state', 'zip',
    'latitude', 'longitude',
    'parcel_id', 'land_use_code', 'land_use_type', 'verification',
    'homestead', 'year_built', 'bedrooms', 'bathrooms',
    'appraised_value', 'annual_tax', 'sale_price', 'sale_date',
]


def main():
    kept = 0
    dropped_inferred = 0
    dropped_non_dwelling = 0
    dropped_vacant = 0
    with open(ENRICHED, newline='') as fin, open(OUT, 'w', newline='') as fout:
        reader = csv.DictReader(fin)
        w = csv.DictWriter(fout, fieldnames=FIELDS)
        w.writeheader()
        for r in reader:
            matched = r.get('match_status') == 'MATCHED'
            lu = (r.get('land_use_code') or '').strip()
            if not matched or lu not in DWELLING:
                if r.get('match_status') != 'MATCHED':
                    dropped_inferred += 1          # Tier 2 / unmatched (guesses)
                elif lu in {'500', '501', '503'}:
                    dropped_vacant += 1
                else:
                    dropped_non_dwelling += 1     # commercial/industrial/exempt
                continue
            number, street = r['number'], r['street']
            unit = (r.get('unit') or '').strip()
            up = f' {unit}' if unit else ''
            w.writerow({
                'address': f'{number} {street}{up}, {CITY}, OH, {ZIP}',
                'number': number, 'street': street, 'unit': unit,
                'city': CITY, 'state': 'OH', 'zip': ZIP,
                'latitude': r.get('latitude', ''), 'longitude': r.get('longitude', ''),
                'parcel_id': r.get('parcel_id', ''), 'land_use_code': lu,
                'land_use_type': r.get('land_use_type', ''),
                'verification': 'auditor_parcel',
                'homestead': r.get('homestead', ''),         # raw recorded value ('Y' or '')
                'year_built': r.get('year_built', ''), 'bedrooms': r.get('bedrooms', ''),
                'bathrooms': r.get('bathrooms', ''),
                'appraised_value': r.get('appraised_value', ''), 'annual_tax': r.get('annual_tax', ''),
                'sale_price': r.get('sale_price', ''), 'sale_date': r.get('sale_date', ''),
            })
            kept += 1
    print(f'CLEAN list (auditor-verified dwellings only): {kept} -> {OUT}')
    print(f'  dropped inferred/unmatched (Tier 2): {dropped_inferred}')
    print(f'  dropped commercial/other (matched, non-dwelling): {dropped_non_dwelling}')
    print(f'  dropped residential-vacant-land: {dropped_vacant}')


if __name__ == '__main__':
    main()
