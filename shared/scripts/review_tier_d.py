#!/usr/bin/env python3
"""Detailed confidence review of Tier D (spatial nearest-parcel) addresses.

For each Tier D address we ask: is the residential parcel we linked it to actually
on the SAME street as the address (=> the address's own building), or a different
street (=> possibly a neighbor)? Plus unit presence and linked land-use type.

Same-street  => high confidence (it's the address's building / a unit in it).
Diff street + unit => medium (apartment; building parcel may carry a parent address).
Diff street + no unit => low (investigate / candidate to drop).
"""
import csv
import glob
import os
import re
from collections import Counter

REPO = '/Users/kevinpatel/Address'
ZIPS = ['43232', '43227', '43207', '43224', '43211', '43004', '43125', '43110', '43147']

SUFFIXES = {'RD', 'DR', 'ST', 'CT', 'LN', 'PL', 'AVE', 'BLVD', 'BV', 'CIR', 'WAY', 'WY',
            'PIKE', 'PK', 'PI', 'HWY', 'TER', 'TERRACE', 'PKWY', 'TRL', 'CV', 'PT', 'BL'}


def street_base(addr):
    """Base street name: uppercase, drop leading number/range, unit, trailing
    directional, and a trailing suffix token if it's a known suffix abbreviation."""
    s = re.sub(r'\s+', ' ', (addr or '').upper()).strip()
    s = re.sub(r'^\d+\s*-\s*\d+\s+', '', s)
    s = re.sub(r'^\d+\s+', '', s)
    s = re.sub(r'\s+(APT|UNIT|STE|SUITE|#)\s*\S*$', '', s)
    s = re.sub(r'\s+[NSEW]$', '', s)
    parts = s.split()
    if parts and parts[-1] in SUFFIXES:
        parts = parts[:-1]
    return ' '.join(parts).strip()


def leading_num(addr):
    m = re.match(r'\s*(\d+)', addr or '')
    return m.group(1) if m else ''


def main():
    pid_parcel = {}
    for f in [f'{REPO}/shared/data/franklin_county_parcels.csv',
              f'{REPO}/shared/data/fairfield_county_parcels.csv']:
        for r in csv.DictReader(open(f, encoding='utf-8-sig')):
            pid_parcel[r['PARCEL ID']] = (r.get('STADDR', ''), r.get('LANDUSE', ''))

    LU_TYPE = {'510': 'SINGLE_FAMILY', '511': 'SINGLE_FAMILY', '512': 'SINGLE_FAMILY',
               '520': 'TWO_FAMILY', '530': 'THREE_FAMILY', '550': 'APARTMENT_4PLUS',
               '551': 'APARTMENT', '552': 'APARTMENT', '553': 'APARTMENT', '559': 'APARTMENT', '560': 'APARTMENT'}

    grand = Counter()
    per_zip = {}
    diff_examples = []

    for zc in ZIPS:
        rf = f'{REPO}/{zc}_project/data/addresses_{zc}_residential_final.csv'
        if not os.path.exists(rf):
            continue
        td = [r for r in csv.DictReader(open(rf)) if 'spatial' in r.get('classification_source', '')]
        cnt = Counter()
        for r in td:
            staddr, lu = pid_parcel.get(r.get('parcel_id', ''), ('', ''))
            same_street = bool(staddr) and street_base(r['street']) == street_base(staddr)
            same_number = bool(staddr) and r.get('number', '').strip() == leading_num(staddr)
            unit = bool((r.get('unit') or '').strip())
            if same_number:
                key = 'HIGH_same_number'          # linked parcel has the same house # -> own parcel
            elif same_street:
                key = 'HIGH_same_street'          # same street, adjacent -> own building
            elif unit:
                key = 'MED_diff_street_unit'      # apartment; building parcel may carry parent addr
            else:
                key = 'LOW_diff_street_no_unit'   # cross-street neighbor -> risky
            cnt[key] += 1
            grand[key] += 1
            if key == 'LOW_diff_street_no_unit' and len(diff_examples) < 15:
                diff_examples.append((zc, r['number'], r['street'], r.get('unit', ''), staddr, LU_TYPE.get(lu, lu)))
        per_zip[zc] = (len(td), cnt)

    print('=== Tier D review (same-street = linked parcel on the address\'s own street) ===\n')
    print(f"{'ZIP':7} {'TierD':7} {'HIGH(#same)':12} {'HIGH(street)':13} {'MED(unit)':10} {'LOW(neighbor)':14}")
    for zc, (tot, cnt) in per_zip.items():
        print(f"{zc:7} {tot:7} {cnt['HIGH_same_number']:12} {cnt['HIGH_same_street']:13} {cnt['MED_diff_street_unit']:10} {cnt['LOW_diff_street_no_unit']:14}")
    print(f"\n{'TOTAL':7} {sum(t for t,_ in per_zip.values()):7} {grand['HIGH_same_number']:12} "
          f"{grand['HIGH_same_street']:13} {grand['MED_diff_street_unit']:10} {grand['LOW_diff_street_no_unit']:14}")
    tot = sum(grand.values()) or 1
    hi = grand['HIGH_same_number']+grand['HIGH_same_street']
    print(f"\nConfidence split: HIGH {hi} ({hi/tot*100:.1f}%) [same# {grand['HIGH_same_number']}, same-st {grand['HIGH_same_street']}] | "
          f"MED {grand['MED_diff_street_unit']} ({grand['MED_diff_street_unit']/tot*100:.1f}%) | "
          f"LOW(neighbor) {grand['LOW_diff_street_no_unit']} ({grand['LOW_diff_street_no_unit']/tot*100:.1f}%)")
    print('\nSample LOW (different street, no unit) — investigate:')
    for zc, num, st, unit, pst, lut in diff_examples:
        print(f"  {zc}  {num} {st:24} -> parcel {pst:28} ({lut})")


if __name__ == '__main__':
    main()
