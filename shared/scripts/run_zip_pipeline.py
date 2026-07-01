#!/usr/bin/env python3
"""End-to-end validated residential-address pipeline for a central-OH ZIP.

Proven 43232 flow (auditor parcel match + Census + spatial nearest-parcel),
consolidated into one reusable script. Outputs:
  <ZIP>_project/data/addresses_<ZIP>_residential_final.csv   (26-col, matches 43213 schema)
  <ZIP>_project/split_addresses_<ZIP>/addresses_<ZIP>_part_NN.csv  (1000/file, Title case, unquoted)

Usage:  python3 run_zip_pipeline.py <ZIP> [CITY]
Boundary ZIPs (43110, 43147) auto-merge oh/fairfield-addresses-county.geojson.
"""
import csv
import io
import json
import math
import os
import re
import sys
import time

import numpy as np
import requests

REPO = '/Users/kevinpatel/Address'
GEOJSON_MAIN = f'{REPO}/oh/franklin-addresses-county.geojson'
PARCELS_FRANKLIN = f'{REPO}/shared/data/franklin_county_parcels.csv'
PARCELS_FAIRFIELD = f'{REPO}/shared/data/fairfield_county_parcels.csv'
CENSUS_URL = 'https://geocoding.geo.census.gov/geocoder/locations/addressbatch'
BOUNDARY_EXTRA = {'43110': ['oh/fairfield-addresses-county.geojson'],
                  '43147': ['oh/fairfield-addresses-county.geojson']}
# ZIPs spanning into Fairfield need Fairfield parcels too
FAIRFIELD_ZIPS = {'43110', '43147'}

DWELLING = {'510', '511', '520', '530', '550', '551', '552', '553', '559', '560'}
VACANT = {'500', '501', '503'}
RES_LAND_USE = DWELLING | VACANT
CENSUS_CHUNK = 4000
SPATIAL_RADIUS_M = 60.0
KEEP = ['PARCEL ID', 'STADDR', 'STHNUM', 'STDIRE', 'STNAME', 'STSFX', 'LANDUSE', 'HOMSTD',
        'OWNER_ADD1', 'NAME1', 'YEARBLT', 'BEDRMS', 'BATHS', 'HBATHS', 'ROOMS', 'APPRTOT',
        'ANN_TAX', 'PRICE', 'TRANDT', 'POINT_X', 'POINT_Y']


def titlecase(s):
    out = []
    for tok in (s or '').split():
        out.append(tok if tok[:1].isdigit()
                   else '-'.join(p.capitalize() if (p and not p[:1].isdigit()) else p for p in tok.split('-')))
    return ' '.join(out)


def normalize_addr(a):
    s = re.sub(r'\s+', ' ', (a or '').upper()).strip()
    s = re.sub(r'\s+(APT|UNIT|STE|SUITE|#)\s*\S*$', '', s)
    s = re.sub(r'^(\d+)\s*-\s*\d+\s+', r'\1 ', s)
    s = re.sub(r'-', ' ', s); s = re.sub(r'\s+', ' ', s).strip()
    for old, new in {' BL': ' BLVD', ' BOULEVARD': ' BLVD', ' AVENUE': ' AVE', ' DRIVE': ' DR',
                     ' STREET': ' ST', ' ROAD': ' RD', ' COURT': ' CT', ' LANE': ' LN',
                     ' PLACE': ' PL', ' CIRCLE': ' CIR', ' PIKE': ' PK', ' TERRACE': ' TER',
                     ' PARKWAY': ' PKWY', ' HIGHWAY': ' HWY', ' TRACE': ' TRCE',
                     ' TRAIL': ' TRL', ' COVE': ' CV', ' POINT': ' PT'}.items():
        if s.endswith(old):
            s = s[:-len(old)] + new
    return re.sub(r'\s+[NSEW]$', '', s)


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


# --- Tier D confidence guard: reject cross-street neighbor matches ---
SUFFIXES = {'RD', 'DR', 'ST', 'CT', 'LN', 'PL', 'AVE', 'BLVD', 'BV', 'CIR', 'WAY', 'WY',
            'PIKE', 'PK', 'PI', 'HWY', 'TER', 'TERRACE', 'PKWY', 'TRL', 'CV', 'PT', 'BL'}


def street_base(addr):
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


def census_batch(rows):
    buf = io.StringIO(); buf.write('id,street,city,state,zip\n')
    for i, st, cy, sp, zp in rows:
        buf.write(f'"{i}","{st}","{cy}","{sp}","{zp}"\n')
    payload = buf.getvalue().encode('utf-8')
    out = {}
    for _ in range(3):
        try:
            r = requests.post(CENSUS_URL, files={'addressFile': ('a.csv', payload, 'text/csv')},
                              data={'benchmark': 'Public_AR_Current'}, timeout=240)
            if r.status_code == 200 and r.text.strip():
                for line in r.text.splitlines():
                    if not line.strip():
                        continue
                    f = next(csv.reader([line])); cid = f[0] if f else ''
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
            print(f'    census batch error: {e}')
        time.sleep(3)
    return out


def census_confirm(rows, zipc):
    """Return the subset of `rows` that Census MATCHes."""
    if not rows:
        return []
    res = {}; batch = []
    for i, a in enumerate(rows):
        st = f"{a['number']} {a['street']}" + (f" {a['unit']}" if a.get('unit') else '')
        batch.append((str(i), st, 'Columbus', 'OH', zipc))
        if len(batch) >= CENSUS_CHUNK:
            res.update(census_batch(batch)); batch = []
    if batch:
        res.update(census_batch(batch))
    return [a for i, a in enumerate(rows) if res.get(str(i), ('No_Match',))[0] == 'Match']


def load_parcels(include_fairfield=False):
    """Build address-key + parcel-id indexes. parcel_xy: pid -> (x, y, county).
    Franklin (Ohio North State Plane) and Fairfield (Ohio South State Plane) are
    tagged separately so the spatial stage can fit per-county affines."""
    sources = [(PARCELS_FRANKLIN, 'franklin')]
    if include_fairfield:
        sources.append((PARCELS_FAIRFIELD, 'fairfield'))
    parcel_lookup = {}; street_lookup = {}; parcels_by_pid = {}; parcel_xy = {}
    for path, county in sources:
        with open(path, newline='', encoding='utf-8-sig') as f:
            for row in csv.DictReader(f):
                s = {k: (row.get(k, '') or '').strip() for k in KEEP}
                s['_county'] = county
                pid = s['PARCEL ID']
                if pid and pid not in parcels_by_pid:
                    parcels_by_pid[pid] = s
                try:
                    parcel_xy[pid] = (float(s['POINT_X']), float(s['POINT_Y']), county)
                except ValueError:
                    pass
                if not s['STHNUM']:
                    continue
                key = normalize_addr(s['STADDR'])
                parcel_lookup.setdefault(key, s)
                rng = re.match(r'^(\d+)\s*-\s*(\d+)\s+(.+)', s['STADDR'])
                if rng:
                    n1, n2, part = rng.groups()
                    for nk in (n1, n2):
                        parcel_lookup.setdefault(normalize_addr(f'{nk} {part}'), s)
                    try:
                        lo, hi = int(n1), int(n2)
                        if hi - lo <= 20:
                            for n in range(lo, hi + 1):
                                parcel_lookup.setdefault(normalize_addr(f'{n} {part}'), s)
                    except ValueError:
                        pass
                sk = normalize_addr(f"{s['STHNUM']} {s['STDIRE']} {s['STNAME']} {s['STSFX']}".strip())
                street_lookup.setdefault(sk, s)
    return parcel_lookup, street_lookup, parcels_by_pid, parcel_xy


def match_addresses(addresses, parcel_lookup, street_lookup):
    for a in addresses:
        number, street = a['number'], re.sub(r'\s+', ' ', a['street']).strip()
        ak = normalize_addr(f'{number} {street}')
        p = parcel_lookup.get(ak)
        if not p and a.get('unit'):
            p = street_lookup.get(ak)
        if not p:
            for pref in ['S ', 'N ', 'E ', 'W ']:
                k = normalize_addr(f'{number} {pref}{street}')
                p = parcel_lookup.get(k) or street_lookup.get(k)
                if p:
                    break
        if not p:
            stripped = re.sub(r'^([SNEW])\s+', '', street)
            if stripped != street:
                k = normalize_addr(f'{number} {stripped}')
                p = parcel_lookup.get(k) or street_lookup.get(k)
        a['parcel'] = p


def spatial_validate(unmatched, enriched, parcels_by_pid, parcel_xy, zipc):
    """Tier D: Census-confirm each unmatched, then link to nearest residential parcel (<=60m).
    Affine fit is per-county so Ohio North (Franklin) and South (Fairfield) State Plane
    coordinate systems are not mixed."""
    unmatched = census_confirm(unmatched, zipc)
    if not unmatched:
        return []
    # group control points by county (parcel_xy now carries county as 3rd element)
    cp = {}
    for a in enriched:
        p = a.get('parcel')
        if not p:
            continue
        pid = p.get('PARCEL ID', '')
        if pid in parcel_xy:
            x, y, co = parcel_xy[pid]
            cp.setdefault(co, []).append((x, y, a['longitude'], a['latitude']))
    # fit affine per county; transform that county's parcel centroids -> lat/lon
    all_pts = []  # (pid, lat, lon)
    for co, pts in cp.items():
        if len(pts) < 10:
            continue
        cX = np.array([p[0] for p in pts]); cY = np.array([p[1] for p in pts])
        clon = np.array([p[2] for p in pts]); clat = np.array([p[3] for p in pts])
        Ain = np.column_stack([cX, cY, np.ones_like(cX)])
        cl = np.linalg.lstsq(Ain, clon, rcond=None)[0]
        cla = np.linalg.lstsq(Ain, clat, rcond=None)[0]
        pids = [p for p in parcel_xy if parcel_xy[p][2] == co and p in parcels_by_pid]
        if not pids:
            continue
        X = np.array([parcel_xy[p][0] for p in pids]); Y = np.array([parcel_xy[p][1] for p in pids])
        Plon = cl[0]*X + cl[1]*Y + cl[2]; Plat = cla[0]*X + cla[1]*Y + cla[2]
        for i, pid in enumerate(pids):
            all_pts.append((pid, float(Plat[i]), float(Plon[i])))
    if not all_pts:
        return []
    Plat = np.array([p[1] for p in all_pts]); Plon = np.array([p[2] for p in all_pts])
    pid_all = [p[0] for p in all_pts]
    alats = np.array([a['latitude'] for a in unmatched]); alons = np.array([a['longitude'] for a in unmatched])
    margin = 0.01
    inbb = (Plat >= alats.min()-margin) & (Plat <= alats.max()+margin) & \
           (Plon >= alons.min()-margin) & (Plon <= alons.max()+margin)
    bidx = np.where(inbb)[0]
    if len(bidx) == 0:
        return []
    Plat_b = Plat[bidx]; Plon_b = Plon[bidx]
    pid_b = [pid_all[i] for i in bidx]; lu_b = [parcels_by_pid[p]['LANDUSE'] for p in pid_b]
    coslat = math.radians(39.9)
    Plat_r = np.radians(Plat_b); Plon_r = np.radians(Plon_b)
    out = []
    for a in unmatched:
        alat_r = math.radians(a['latitude']); alon_r = math.radians(a['longitude'])
        dx = (Plon_r - alon_r) * math.cos(coslat) * 6371000.0
        dy = (Plat_r - alat_r) * 6371000.0
        j = int(np.argmin(dx*dx + dy*dy))
        dist = math.sqrt(dx[j]**2 + dy[j]**2)
        if dist <= SPATIAL_RADIUS_M and lu_b[j] in DWELLING:
            # confidence guard: only accept if linked parcel is own parcel/building
            # (same house # or same street) or the address is an apartment unit.
            p = parcels_by_pid[pid_b[j]]
            pst = p.get('STADDR', '')
            same_num = bool(pst) and a['number'].strip() == leading_num(pst)
            same_st = bool(pst) and street_base(a['street']) == street_base(pst)
            has_unit = bool((a.get('unit') or '').strip())
            if same_num or same_st or has_unit:
                a['parcel'] = p
                out.append(a)
    return out


def main():
    if len(sys.argv) < 2:
        sys.exit('Usage: run_zip_pipeline.py <ZIP> [CITY]')
    ZIP = sys.argv[1]
    CITY = sys.argv[2] if len(sys.argv) > 2 else 'Columbus'
    sources = [GEOJSON_MAIN] + [f'{REPO}/{s}' for s in BOUNDARY_EXTRA.get(ZIP, [])]
    PROJ = f'{REPO}/{ZIP}_project'; DATA = f'{PROJ}/data'; SPLIT = f'{PROJ}/split_addresses_{ZIP}'
    os.makedirs(DATA, exist_ok=True); os.makedirs(SPLIT, exist_ok=True)
    print(f'=== Pipeline: ZIP {ZIP} (city {CITY}), sources {[os.path.basename(s) for s in sources]} ===')

    print('\n[1/6] Extract from GeoJSON...')
    seen = set(); addresses = []
    for src in sources:
        with open(src) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    feat = json.loads(line)
                except Exception:
                    continue
                props = feat.get('properties', {})
                if (props.get('postcode') or '').strip() != ZIP:
                    continue
                number = (props.get('number') or '').strip()
                street = re.sub(r'\s+', ' ', (props.get('street') or '')).strip()
                if not number or not street:
                    continue
                unit = (props.get('unit') or '').strip()
                key = f'{number}|{street}|{unit}'
                if key in seen:
                    continue
                seen.add(key)
                coords = feat.get('geometry', {}).get('coordinates', [0, 0])
                addresses.append({'number': number, 'street': street, 'unit': unit,
                                  'city': (props.get('city') or CITY).strip() or CITY,
                                  'latitude': coords[1] if len(coords) > 1 else 0.0,
                                  'longitude': coords[0] if coords else 0.0})
    print(f'    unique addresses: {len(addresses)}')

    include_ff = ZIP in FAIRFIELD_ZIPS
    print(f'\n[2/6] Load parcels (Franklin{" + Fairfield" if include_ff else ""}) + match...')
    parcel_lookup, street_lookup, parcels_by_pid, parcel_xy = load_parcels(include_fairfield=include_ff)
    match_addresses(addresses, parcel_lookup, street_lookup)
    matched = sum(1 for a in addresses if a.get('parcel'))
    print(f'    parcel-matched: {matched} / {len(addresses)}')

    print('\n[3/6] Tier A = matched dwelling + Census...')
    dwell = [a for a in addresses if a.get('parcel') and a['parcel']['LANDUSE'] in DWELLING]
    resA = census_confirm(dwell, ZIP)
    print(f'    dwellings: {len(dwell)} | Tier A (Census-confirmed): {len(resA)}')

    print('\n[4/6] Tier D = spatial nearest-parcel + Census...')
    unmatched = [a for a in addresses if not a.get('parcel')]
    tierD = spatial_validate(unmatched, addresses, parcels_by_pid, parcel_xy, ZIP)
    print(f'    Tier D: {len(tierD)}')

    print('\n[5/6] Write residential_final (26-col)...')
    out_fields = ['address', 'number', 'street', 'unit', 'city', 'state', 'zip', 'latitude', 'longitude',
                  'final_classification', 'classification_source', 'google_validated_address', 'google_city',
                  'parcel_id', 'land_use_code', 'land_use_type', 'occupancy', 'owner_name', 'homestead',
                  'year_built', 'bedrooms', 'bathrooms', 'appraised_value', 'annual_tax', 'sale_price', 'sale_date']
    final_path = f'{DATA}/addresses_{ZIP}_residential_final.csv'
    with open(final_path, 'w', newline='') as fout:
        w = csv.DictWriter(fout, fieldnames=out_fields); w.writeheader()
        for a, source in [(a, 'auditor_parcel_address_match') for a in resA] + \
                         [(a, 'auditor_parcel_spatial_match') for a in tierD]:
            p = a['parcel']; unit = a.get('unit', ''); up = f' {unit}' if unit else ''
            w.writerow({'address': f"{a['number']} {a['street']}{up}, {CITY.upper()}, OH, {ZIP}",
                        'number': a['number'], 'street': a['street'], 'unit': unit,
                        'city': CITY.title(), 'state': 'OH', 'zip': ZIP,
                        'latitude': a['latitude'], 'longitude': a['longitude'],
                        'final_classification': 'RESIDENTIAL', 'classification_source': source,
                        'google_validated_address': '', 'google_city': '',
                        'parcel_id': p.get('PARCEL ID', ''), 'land_use_code': p.get('LANDUSE', ''),
                        'land_use_type': classify_land_use(p.get('LANDUSE', '')),
                        'occupancy': classify_occupancy(p), 'owner_name': p.get('NAME1', ''),
                        'homestead': p.get('HOMSTD', ''), 'year_built': p.get('YEARBLT', ''),
                        'bedrooms': p.get('BEDRMS', ''), 'bathrooms': p.get('BATHS', ''),
                        'appraised_value': p.get('APPRTOT', ''), 'annual_tax': p.get('ANN_TAX', ''),
                        'sale_price': p.get('PRICE', ''), 'sale_date': p.get('TRANDT', '')})

    print('\n[6/6] Split into 1000-row shards (Title case, unquoted)...')
    rows = list(csv.DictReader(open(final_path, newline='')))
    chunk = []; file_no = 0
    for r in rows:
        unit = (r.get('unit') or '').strip(); up = f' {titlecase(unit)}' if unit else ''
        chunk.append(f"{r['number']} {titlecase(r['street'])}{up}, {CITY.title()}, OH, {ZIP}")
        if len(chunk) >= 1000:
            file_no += 1
            with open(f'{SPLIT}/addresses_{ZIP}_part_{file_no:02d}.csv', 'w', newline='') as sf:
                sf.write('address\n'); sf.writelines(l + '\n' for l in chunk)
            chunk = []
    if chunk:
        file_no += 1
        with open(f'{SPLIT}/addresses_{ZIP}_part_{file_no:02d}.csv', 'w', newline='') as sf:
            sf.write('address\n'); sf.writelines(l + '\n' for l in chunk)

    n_final = len(resA) + len(tierD)
    print(f'\n=== {ZIP} FUNNEL ===')
    print(f'  unique addresses : {len(addresses)}')
    print(f'  parcel-matched   : {matched}')
    print(f'  Tier A (parcel+Census) : {len(resA)}')
    print(f'  Tier D (spatial+Census): {len(tierD)}')
    print(f'  FINAL validated  : {n_final}  ({n_final/max(len(addresses),1)*100:.1f}% of source)')
    print(f'  -> {final_path}')
    print(f'  -> {SPLIT}/ ({file_no} shard files)')


if __name__ == '__main__':
    main()
