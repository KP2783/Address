#!/usr/bin/env python3
"""Recover additional residential addresses from 43232's unverified pool.

The unverified addresses are mostly condo/apartment complexes whose GeoJSON
unit-numbering (2, 4, 6...) can't be matched to auditor parcel street-numbers
(5911, 5933...). Recovery strategy, two independent checks, no guesses:
  1. CENSUS: batch-validate each address. Census MATCH => the address is a real,
     federally-recognized (mailable) address.
  2. RESIDENTIAL: only keep Census matches whose STREET is residential per the
     auditor parcel file (>=70% dwelling land-use among parcels on that street,
     >=3 parcels). Auditor confirms the complex is residential; Census confirms
     this specific address exists.

Outputs:
  recovered_43232.csv            (Census-confirmed + auditor-residential-street)
  unrecoverable_43232.csv        (Census did not match, or street not residential)
"""
import csv
import io
import os
import re
import time
import requests

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, '..', 'data')
ZIP = '43232'
CITY = 'Columbus'

ENRICHED = os.path.join(DATA_DIR, f'addresses_{ZIP}_enriched.csv')
PARCELS_FULL = '/Users/kevinpatel/Address/shared/data/franklin_county_parcels.csv'
RECOVERED = os.path.join(DATA_DIR, f'recovered_{ZIP}.csv')
UNRECOVERABLE = os.path.join(DATA_DIR, f'unrecoverable_{ZIP}.csv')

URL = 'https://geocoding.geo.census.gov/geocoder/locations/addressbatch'
CHUNK = 4000
THRESHOLD = 0.70
MIN_PARCELS = 3
DWELLING = {'510', '511', '520', '530', '550', '551', '552', '553', '559', '560'}


def street_key(name, sfx=''):
    s = f'{name} {sfx}'.upper().strip()
    s = re.sub(r'-', ' ', s); s = re.sub(r'\s+', ' ', s).strip()
    full = {'WY': 'WAY', 'PL': 'PLACE', 'CT': 'COURT', 'LN': 'LANE', 'DR': 'DRIVE',
            'RD': 'ROAD', 'ST': 'STREET', 'AVE': 'AVENUE', 'CIR': 'CIRCLE',
            'BLVD': 'BOULEVARD', 'PK': 'PIKE', 'TER': 'TERRACE', 'PKWY': 'PARKWAY',
            'HWY': 'HIGHWAY', 'TRL': 'TRAIL', 'CV': 'COVE', 'PT': 'POINT'}
    for ab, ful in full.items():
        s = re.sub(r'\b' + ab + r'$', ful, s)
    s = re.sub(r'\s+[NSEW]$', '', s)
    s = re.sub(r'^([SNEW])\s+', '', s)
    return s


def build_street_signal():
    sig = {}
    with open(PARCELS_FULL, newline='', encoding='utf-8-sig') as f:
        for row in csv.DictReader(f):
            stn = (row.get('STNAME', '') or '').strip()
            if not stn:
                continue
            k = street_key(stn, row.get('STSFX', ''))
            d, t = sig.get(k, (0, 0))
            sig[k] = (d + (1 if (row.get('LANDUSE', '') or '').strip() in DWELLING else 0), t + 1)
    return sig


def census_batch(rows):
    buf = io.StringIO()
    buf.write('id,street,city,state,zip\n')
    for i, st, cy, sp, zp in rows:
        buf.write(f'"{i}","{st}","{cy}","{sp}","{zp}"\n')
    payload = buf.getvalue().encode('utf-8')
    out = {}
    for attempt in range(3):
        try:
            r = requests.post(URL, files={'addressFile': ('a.csv', payload, 'text/csv')},
                              data={'benchmark': 'Public_AR_Current'}, timeout=240)
            if r.status_code == 200 and r.text.strip():
                for line in r.text.splitlines():
                    if not line.strip():
                        continue
                    f = next(csv.reader([line]))
                    cid = f[0] if f else ''
                    status = 'No_Match'; matched = None
                    for idx, val in enumerate(f):
                        if val in ('Match', 'No_Match', 'Tie'):
                            status = val
                            if status == 'Match' and idx + 1 < len(f):
                                matched = f[idx + 1]
                            break
                    out[cid] = (status, matched)
                return out
        except Exception as e:
            print(f'  batch error (attempt {attempt+1}): {e}')
        time.sleep(3)
    return out


def main():
    print('Building street residential signal...')
    sig = build_street_signal()

    pool = [r for r in csv.DictReader(open(ENRICHED, newline='')) if r['match_status'] != 'MATCHED']
    print(f'Unverified pool: {len(pool)} addresses -> Census-validating...')

    results = {}
    batch = []
    for i, r in enumerate(pool):
        st = f"{r['number']} {r['street']}" + (f" {r['unit']}" if (r.get('unit') or '').strip() else '')
        batch.append((str(i), st, CITY, 'OH', ZIP))
        if len(batch) >= CHUNK:
            print(f'  batch of {len(batch)}...')
            results.update(census_batch(batch)); batch = []
    if batch:
        results.update(census_batch(batch))

    n_match = n_residential = n_notres = n_nomatch = 0
    fields = ['address', 'number', 'street', 'unit', 'city', 'state', 'zip',
              'latitude', 'longitude', 'final_classification', 'existence_source',
              'residential_source', 'census_matched_address']
    with open(RECOVERED, 'w', newline='') as fr, open(UNRECOVERABLE, 'w', newline='') as fu:
        wr = csv.DictWriter(fr, fieldnames=fields); wr.writeheader()
        wu = csv.DictWriter(fu, fieldnames=['number', 'street', 'unit', 'census_status', 'street_residential_signal'])
        wu.writeheader()
        for i, r in enumerate(pool):
            st, matched = results.get(str(i), ('MISSING', None))
            unit = (r.get('unit') or '').strip()
            up = f' {unit}' if unit else ''
            if st == 'Match':
                n_match += 1
                dwell, tot = sig.get(street_key(r['street']), (0, 0))
                residential = tot >= MIN_PARCELS and dwell / tot >= THRESHOLD
                if residential:
                    n_residential += 1
                    wr.writerow({
                        'address': f"{r['number']} {r['street']}{up}, {CITY}, OH, {ZIP}",
                        'number': r['number'], 'street': r['street'], 'unit': unit,
                        'city': CITY, 'state': 'OH', 'zip': ZIP,
                        'latitude': r.get('latitude', ''), 'longitude': r.get('longitude', ''),
                        'final_classification': 'RESIDENTIAL',
                        'existence_source': 'census_geocoder',
                        'residential_source': f'auditor_street ({dwell}/{tot} dwelling)',
                        'census_matched_address': matched or '',
                    })
                else:
                    n_notres += 1
                    wu.writerow({'number': r['number'], 'street': r['street'], 'unit': unit,
                                 'census_status': 'Match', 'street_residential_signal': f'{dwell}/{tot}'})
            else:
                n_nomatch += 1
                dwell, tot = sig.get(street_key(r['street']), (0, 0))
                wu.writerow({'number': r['number'], 'street': r['street'], 'unit': unit,
                             'census_status': st, 'street_residential_signal': f'{dwell}/{tot}'})

    print(f'\nPool: {len(pool)}')
    print(f'  Census MATCHED: {n_match} ({n_match/len(pool)*100:.1f}%)')
    print(f'    of which residential (auditor street): {n_residential}')
    print(f'    of which NOT residential street:       {n_notres}')
    print(f'  Census NOT matched: {n_nomatch}')
    print(f'\nRECOVERED residential: {n_residential} -> {RECOVERED}')
    print(f'Unrecoverable: {n_match - n_residential + n_nomatch} -> {UNRECOVERABLE}')


if __name__ == '__main__':
    main()
