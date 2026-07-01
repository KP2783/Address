#!/usr/bin/env python3
"""Spatially validate 43232's un-matched addresses against their NEAREST parcel.

Why: condo/apartment units can't be address-string-matched to parcels (different
numbering), so they were left unvalidated. But every address has a lat/lon and
every parcel has a centroid (POINT_X/POINT_Y in Ohio State Plane feet). We:

  1. Fit an affine transform State-Plane(X,Y) -> WGS84(lat,lon) using the already
     matched Tier-A addresses as control points (their parcel centroid <-> their
     known address lat/lon). Local affine over a single ZIP is sub-meter accurate.
  2. Transform all parcel centroids to lat/lon.
  3. For each UNMATCHED address, find the nearest parcel centroid within a radius.
     That parcel's true LANDUSE validates whether the address is residential.

This is authoritative (links each address to a real parcel's recorded land use),
no inference. Addresses whose nearest residential-coded parcel is within radius
are VALIDATED residential -> validated_residential_43232.csv.
"""
import csv
import math
import os

import numpy as np

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, '..', 'data')
ZIP = '43232'

ENRICHED = os.path.join(DATA_DIR, f'addresses_{ZIP}_enriched.csv')
PARCELS_FULL = '/Users/kevinpatel/Address/shared/data/franklin_county_parcels.csv'
OUT_VALIDATED = os.path.join(DATA_DIR, f'validated_residential_{ZIP}.csv')
OUT_REVIEW = os.path.join(DATA_DIR, f'spatial_review_{ZIP}.csv')

DWELLING = {'510', '511', '520', '530', '550', '551', '552', '553', '559', '560'}
VACANT = {'500', '501', '503'}
RADIUS_M = 60.0  # max distance to accept nearest parcel as the address's parcel


def haversine_m(lat1, lon1, lat2, lon2):
    R = 6371000.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
    return 2*R*math.asin(math.sqrt(a))


def main():
    # 1. Load parcels: id -> (X, Y, LANDUSE)
    print('Loading parcel centroids...')
    parcels = {}
    with open(PARCELS_FULL, newline='', encoding='utf-8-sig') as f:
        for row in csv.DictReader(f):
            pid = (row.get('PARCEL ID', '') or '').strip()
            x = (row.get('POINT_X', '') or '').strip()
            y = (row.get('POINT_Y', '') or '').strip()
            lu = (row.get('LANDUSE', '') or '').strip()
            if pid and x and y:
                try:
                    parcels[pid] = (float(x), float(y), lu)
                except ValueError:
                    pass
    print(f'  parcels with coords: {len(parcels)}')

    # 2. Control points from matched Tier-A addresses
    ctl_X, ctl_Y, ctl_lon, ctl_lat = [], [], [], []
    unmatched = []
    for r in csv.DictReader(open(ENRICHED, newline='')):
        try:
            alat, alon = float(r['latitude']), float(r['longitude'])
        except (ValueError, KeyError):
            continue
        if r['match_status'] == 'MATCHED':
            p = parcels.get((r.get('parcel_id', '') or '').strip())
            if p:
                ctl_X.append(p[0]); ctl_Y.append(p[1]); ctl_lon.append(alon); ctl_lat.append(alat)
        else:
            unmatched.append(r)
    ctl_X = np.array(ctl_X); ctl_Y = np.array(ctl_Y)
    ctl_lon = np.array(ctl_lon); ctl_lat = np.array(ctl_lat)
    print(f'  control points (matched parcels): {len(ctl_X)} | unmatched to validate: {len(unmatched)}')

    # 3. Affine fit: [lon, lat] = A @ [X, Y, 1]
    A_in = np.column_stack([ctl_X, ctl_Y, np.ones_like(ctl_X)])
    coefs_lon, res1, *_ = np.linalg.lstsq(A_in, ctl_lon, rcond=None)
    coefs_lat, res2, *_ = np.linalg.lstsq(A_in, ctl_lat, rcond=None)
    # fit residual in meters
    pred_lon = A_in @ coefs_lon; pred_lat = A_in @ coefs_lat
    resid_m = np.array([haversine_m(ctl_lat[i], ctl_lon[i], pred_lat[i], pred_lon[i]) for i in range(len(ctl_lat))])
    print(f'  affine fit residual: mean {resid_m.mean():.1f} m, median {np.median(resid_m):.1f} m, p95 {np.percentile(resid_m,95):.1f} m')

    # 4. Transform all parcel centroids -> lat/lon
    allpid = list(parcels.keys())
    X = np.array([parcels[p][0] for p in allpid])
    Y = np.array([parcels[p][1] for p in allpid])
    LU = [parcels[p][2] for p in allpid]
    Plon = coefs_lon[0]*X + coefs_lon[1]*Y + coefs_lon[2]
    Plat = coefs_lat[0]*X + coefs_lat[1]*Y + coefs_lat[2]

    # 5. Bounding box around 43232 unmatched addresses (+margin)
    alats = np.array([float(r['latitude']) for r in unmatched])
    alons = np.array([float(r['longitude']) for r in unmatched])
    margin = 0.01
    latmin, latmax = alats.min()-margin, alats.max()+margin
    lonmin, lonmax = alons.min()-margin, alons.max()+margin
    in_bbox = (Plat >= latmin) & (Plat <= latmax) & (Plon >= lonmin) & (Plon <= lonmax)
    bidx = np.where(in_bbox)[0]
    print(f'  parcels in 43232 bbox: {len(bidx)}')

    Plat_b = Plat[bidx]; Plon_b = Plon[bidx]; LU_b = [LU[i] for i in bidx]
    coslat = math.radians(39.9)
    Plat_r = np.radians(Plat_b); Plon_r = np.radians(Plon_b)

    # 6. Nearest parcel for each unmatched address
    validated = 0
    counts = {'residential': 0, 'commercial': 0, 'vacant': 0, 'other': 0, 'no_nearby': 0}
    with open(OUT_VALIDATED, 'w', newline='') as fv, open(OUT_REVIEW, 'w', newline='') as fr:
        fv_fields = ['address', 'number', 'street', 'unit', 'city', 'state', 'zip',
                     'latitude', 'longitude', 'residential_proof', 'nearest_parcel_land_use',
                     'distance_m', 'parcel_id']
        rv_fields = ['number', 'street', 'unit', 'nearest_parcel_land_use', 'distance_m', 'reason']
        wv = csv.DictWriter(fv, fieldnames=fv_fields); wv.writeheader()
        wr = csv.DictWriter(fr, fieldnames=rv_fields); wr.writeheader()

        for r in unmatched:
            alat, alon = float(r['latitude']), float(r['longitude'])
            alat_r, alon_r = math.radians(alat), math.radians(alon)
            dx = (Plon_r - alon_r) * math.cos(coslat) * 6371000.0
            dy = (Plat_r - alat_r) * 6371000.0
            d2 = dx*dx + dy*dy
            j = int(np.argmin(d2))
            dist = math.sqrt(d2[j])
            lu = LU_b[j]
            unit = (r.get('unit') or '').strip()
            up = f' {unit}' if unit else ''
            addr = f"{r['number']} {r['street']}{up}, Columbus, OH, {ZIP}"
            if dist <= RADIUS_M:
                if lu in DWELLING:
                    counts['residential'] += 1; validated += 1
                    wv.writerow({'address': addr, 'number': r['number'], 'street': r['street'],
                                 'unit': unit, 'city': 'Columbus', 'state': 'OH', 'zip': ZIP,
                                 'latitude': alat, 'longitude': alon,
                                 'residential_proof': f'nearest parcel (within {dist:.0f}m) LANDUSE {lu}',
                                 'nearest_parcel_land_use': lu, 'distance_m': f'{dist:.1f}',
                                 'parcel_id': allpid[bidx[j]]})
                elif lu in VACANT:
                    counts['vacant'] += 1
                    wr.writerow({'number': r['number'], 'street': r['street'], 'unit': unit,
                                 'nearest_parcel_land_use': lu, 'distance_m': f'{dist:.1f}', 'reason': 'nearest=vacant land'})
                else:
                    counts['commercial' if (lu[:1] in ('3', '4')) else 'other'] += 1
                    wr.writerow({'number': r['number'], 'street': r['street'], 'unit': unit,
                                 'nearest_parcel_land_use': lu, 'distance_m': f'{dist:.1f}',
                                 'reason': f'nearest non-residential ({lu})'})
            else:
                counts['no_nearby'] += 1
                wr.writerow({'number': r['number'], 'street': r['street'], 'unit': unit,
                             'nearest_parcel_land_use': lu, 'distance_m': f'{dist:.1f}',
                             'reason': f'nearest parcel {dist:.0f}m away (> {RADIUS_M:.0f}m)'})

    print(f'\nUnmatched addresses: {len(unmatched)}')
    for k, v in counts.items():
        print(f'  {k:12}: {v}')
    print(f'\nVALIDATED residential (nearest residential parcel within {RADIUS_M:.0f}m): {validated}')
    print(f'  -> {OUT_VALIDATED}')


if __name__ == '__main__':
    main()
