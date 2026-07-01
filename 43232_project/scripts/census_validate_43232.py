#!/usr/bin/env python3
"""Census legitimacy check for the 43232 clean list.

POSTs addresses in batches to the US Census Geocoder (locations/addressbatch).
An address that Census MATCHES is independently confirmed to exist as a real,
federally-recognized address — the second authoritative source alongside the
auditor parcel. Anything Census does NOT match is excluded from the final
'completely legit' list and written to census_review_43232.csv for follow-up.

Outputs:
  addresses_43232_clean_validated.csv  (auditor-verified dwelling AND Census-matched)
  census_review_43232.csv              (Census did not match -> not in final list)
"""
import csv
import io
import os
import sys
import time

import requests

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, '..', 'data')
ZIP = '43232'
CLEAN = os.path.join(DATA_DIR, f'addresses_{ZIP}_clean.csv')
VALIDATED = os.path.join(DATA_DIR, f'addresses_{ZIP}_clean_validated.csv')
REVIEW = os.path.join(DATA_DIR, f'census_review_{ZIP}.csv')

URL = 'https://geocoding.geo.census.gov/geocoder/locations/addressbatch'
BENCHMARK = 'Public_AR_Current'
CHUNK = 4000  # Census accepts up to 10k; keep chunks comfortable


def census_batch(rows):
    """rows: list of (id, street, city, state, zip). Returns dict id->('Match'|'No_Match'|'Tie', matched_addr_or_None)."""
    buf = io.StringIO()
    buf.write('id,street,city,state,zip\n')
    for i, st, cy, sp, zp in rows:
        # quote fields that may contain commas
        buf.write(f'"{i}","{st}","{cy}","{sp}","{zp}"\n')
    payload = buf.getvalue().encode('utf-8')
    files = {'addressFile': ('addresses.csv', payload, 'text/csv')}
    data = {'benchmark': BENCHMARK}
    out = {}
    for attempt in range(3):
        try:
            r = requests.post(URL, files=files, data=data, timeout=240)
            if r.status_code == 200 and r.text.strip():
                for line in r.text.splitlines():
                    if not line.strip():
                        continue
                    f = next(csv.reader([line]))
                    if not f:
                        continue
                    cid = f[0]
                    status = 'No_Match'
                    matched = None
                    for idx, val in enumerate(f):
                        if val in ('Match', 'No_Match', 'Tie'):
                            status = val
                            if status == 'Match' and idx + 1 < len(f):
                                matched = f[idx + 1]
                            break
                    out[cid] = (status, matched)
                return out
            print(f'  batch http {r.status_code}, len={len(r.text)} (attempt {attempt+1})')
        except Exception as e:
            print(f'  batch error (attempt {attempt+1}): {e}')
        time.sleep(3)
    return out


def main():
    rows_in = list(csv.DictReader(open(CLEAN, newline='')))
    print(f'Validating {len(rows_in)} addresses against US Census Geocoder...')

    results = {}  # id -> (status, matched)
    batch = []
    for i, r in enumerate(rows_in):
        st = f"{r['number']} {r['street']}" + (f" {r['unit']}" if r['unit'] else '')
        batch.append((str(i), st, r['city'], r['state'], r['zip']))
        if len(batch) >= CHUNK:
            print(f'  batch of {len(batch)}...')
            results.update(census_batch(batch))
            batch = []
    if batch:
        results.update(census_batch(batch))

    fields = list(rows_in[0].keys()) + ['census_match', 'census_matched_address']
    n_match = n_nomatch = n_missing = 0
    with open(VALIDATED, 'w', newline='') as fv, open(REVIEW, 'w', newline='') as fr:
        wv = csv.DictWriter(fv, fieldnames=fields)
        wr = csv.DictWriter(fr, fieldnames=['number', 'street', 'unit', 'city', 'state', 'zip', 'census_status'])
        wv.writeheader(); wr.writeheader()
        for i, r in enumerate(rows_in):
            st, matched = results.get(str(i), ('MISSING', None))
            if st == 'Match':
                n_match += 1
                r2 = dict(r); r2['census_match'] = 'Y'; r2['census_matched_address'] = matched or ''
                wv.writerow(r2)
            else:
                n_nomatch += 1
                wr.writerow({'number': r['number'], 'street': r['street'], 'unit': r['unit'],
                             'city': r['city'], 'state': r['state'], 'zip': r['zip'],
                             'census_status': st})

    total = len(rows_in)
    print(f'\nCensus results: MATCH={n_match} ({n_match/total*100:.1f}%)  '
          f'NOT-MATCHED={n_nomatch} ({n_nomatch/total*100:.1f}%)')
    print(f'FINAL legit list: {VALIDATED}  ({n_match} rows)')
    print(f'Sent to review (Census not matched): {REVIEW}  ({n_nomatch} rows)')


if __name__ == '__main__':
    main()
