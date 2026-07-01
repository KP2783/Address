#!/usr/bin/env python3
"""Combine 43232 legit tiers into one labeled list.

TIER A (highest): auditor parcel-verified dwelling + Census-confirmed.
TIER B (high):     Census-confirmed + auditor street is residential (condo/apartment
                   complexes where units can't be number-matched to parcels, but the
                   street is residential and the address is Census-real).

Tier C (apartment units Census-confirmed but on non-dwelling-coded streets) is left
separate in apartment_units_review_43232.csv as an OPT-IN tier — real addresses,
but residential status is inferred (unit => apartment), not auditor-verified.
"""
import csv
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, '..', 'data')
ZIP = '43232'

A = os.path.join(DATA_DIR, f'addresses_{ZIP}_clean_validated.csv')   # 9934
B = os.path.join(DATA_DIR, f'recovered_{ZIP}.csv')                   # 1876
UNREC = os.path.join(DATA_DIR, f'unrecoverable_{ZIP}.csv')           # census match/not-res + no-match
OUT = os.path.join(DATA_DIR, f'addresses_{ZIP}_legit.csv')
APT_REVIEW = os.path.join(DATA_DIR, f'apartment_units_review_{ZIP}.csv')

OUT_FIELDS = ['tier', 'address', 'number', 'street', 'unit', 'city', 'state', 'zip',
              'latitude', 'longitude', 'residential_proof', 'existence_proof',
              'parcel_id', 'land_use_type', 'homestead', 'census_matched_address']


def main():
    n_a = n_b = 0
    with open(OUT, 'w', newline='') as fout, open(APT_REVIEW, 'w', newline='') as fapt:
        w = csv.DictWriter(fout, fieldnames=OUT_FIELDS); w.writeheader()
        wa = csv.DictWriter(fapt, fieldnames=['address', 'number', 'street', 'unit', 'city', 'state', 'zip',
                                              'note']); wa.writeheader()
        # Tier A
        for r in csv.DictReader(open(A, newline='')):
            n_a += 1
            w.writerow({
                'tier': 'A_parcel_and_census',
                'address': r['address'], 'number': r['number'], 'street': r['street'],
                'unit': r['unit'], 'city': r['city'], 'state': r['state'], 'zip': r['zip'],
                'latitude': r['latitude'], 'longitude': r['longitude'],
                'residential_proof': f"auditor parcel {r['parcel_id']} ({r['land_use_type']})",
                'existence_proof': 'auditor parcel + census geocoder',
                'parcel_id': r['parcel_id'], 'land_use_type': r['land_use_type'],
                'homestead': r.get('homestead', ''), 'census_matched_address': r.get('census_matched_address', ''),
            })
        # Tier B
        for r in csv.DictReader(open(B, newline='')):
            n_b += 1
            w.writerow({
                'tier': 'B_census_and_residential_street',
                'address': r['address'], 'number': r['number'], 'street': r['street'],
                'unit': r['unit'], 'city': r['city'], 'state': r['state'], 'zip': r['zip'],
                'latitude': r['latitude'], 'longitude': r['longitude'],
                'residential_proof': r['residential_source'],
                'existence_proof': 'census geocoder (no parcel match)',
                'parcel_id': '', 'land_use_type': '', 'homestead': '',
                'census_matched_address': r.get('census_matched_address', ''),
            })
        # Apartment-unit opt-in tier (Census-confirmed, has unit, but street not dwelling-coded)
        n_apt = 0
        for r in csv.DictReader(open(UNREC, newline='')):
            if r['census_status'] == 'Match' and (r.get('unit') or '').strip():
                n_apt += 1
                up = f" {r['unit']}"
                wa.writerow({
                    'address': f"{r['number']} {r['street']}{up}, Columbus, OH, {ZIP}",
                    'number': r['number'], 'street': r['street'], 'unit': r['unit'],
                    'city': 'Columbus', 'state': 'OH', 'zip': ZIP,
                    'note': 'census-confirmed apartment unit; residential inferred (unit), not auditor-verified',
                })

    print(f'TIER A (auditor parcel + Census): {n_a}')
    print(f'TIER B (Census + residential street): {n_b}')
    print(f'LEGIT LIST (A+B): {n_a + n_b} -> {OUT}')
    print(f'Optional apartment-unit tier (Census-real, residential inferred): {n_apt} -> {APT_REVIEW}')


if __name__ == '__main__':
    main()
