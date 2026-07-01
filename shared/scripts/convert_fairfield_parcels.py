#!/usr/bin/env python3
"""Convert Fairfield County parcel shapefile -> Franklin-compatible CSV.

Maps Fairfield columns to the names the pipeline expects (STADDR, LANDUSE, etc.)
and computes a parcel centroid (mean of polygon vertices) for the spatial stage.
Fairfield land-use codes match Franklin's scheme (510/511 SF, 550 apts, 500 vacant).
Output: shared/data/fairfield_county_parcels.csv
"""
import csv
import glob
import os
import shapefile

REPO = '/Users/kevinpatel/Address'
SHP = glob.glob(f'{REPO}/shared/data/fairfield_parcels/parcels.shp')[0]
OUT = f'{REPO}/shared/data/fairfield_county_parcels.csv'

# Franklin-compatible output columns
FIELDS = ['PARCEL ID', 'STADDR', 'STHNUM', 'STDIRE', 'STNAME', 'STSFX', 'LANDUSE',
          'HOMSTD', 'OWNER_ADD1', 'NAME1', 'YEARBLT', 'BEDRMS', 'BATHS', 'HBATHS',
          'ROOMS', 'APPRTOT', 'ANN_TAX', 'PRICE', 'TRANDT', 'POINT_X', 'POINT_Y']


def centroid(shape):
    pts = shape.points
    if not pts:
        return None, None
    # use the largest part (parcel polygons may be multipart)
    parts = list(shape.parts) + [len(pts)]
    best = max(range(len(shape.parts)), key=lambda i: parts[i+1] - parts[i]) if shape.parts else 0
    s = parts[best]; e = parts[best+1]
    seg = pts[s:e]
    if not seg:
        seg = pts
    n = len(seg)
    return sum(p[0] for p in seg)/n, sum(p[1] for p in seg)/n


def s(v):
    if v is None:
        return ''
    if hasattr(v, 'isoformat'):
        return v.isoformat()
    return str(v)


def main():
    sf = shapefile.Reader(SHP, encoding='latin-1')
    shapes = sf.shapes()
    n = 0; n_res = 0; n_xy = 0
    DWELLING = {'510', '511', '512', '520', '530', '550', '551', '552', '553', '559', '560'}
    with open(OUT, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        for i, rec in enumerate(sf.records()):
            d = rec.as_dict()
            paddr = s(d.get('PADDR1', '')).strip()
            if not paddr:
                continue
            cx, cy = (None, None)
            try:
                cx, cy = centroid(shapes[i])
            except Exception:
                pass
            lu = s(d.get('LUC', '')).strip()
            if lu in DWELLING:
                n_res += 1
            row = {
                'PARCEL ID': s(d.get('PARID', '') or d.get('PIN', '')),
                'STADDR': paddr,
                'STHNUM': s(d.get('ADRNO', '')).replace('.0', ''),
                'STDIRE': s(d.get('ADRDIR', '')),
                'STNAME': s(d.get('ADRSTR', '')),
                'STSFX': s(d.get('ADRSUF', '')),
                'LANDUSE': lu,
                'HOMSTD': '',                       # not in Fairfield shapefile
                'OWNER_ADD1': s(d.get('MADDR1', '')),
                'NAME1': s(d.get('OWN1', '')),
                'YEARBLT': s(d.get('YRBLT', '')),
                'BEDRMS': s(d.get('RMBED', '')),
                'BATHS': s(d.get('FIXBATH', '')),
                'HBATHS': s(d.get('FIXHALF', '')),
                'ROOMS': s(d.get('RMTOT', '')),
                'APPRTOT': s(d.get('APPRVAL', '')),
                'ANN_TAX': '',                      # not in Fairfield shapefile
                'PRICE': s(d.get('PRICE', '')),
                'TRANDT': s(d.get('SALEDT', '')),
                'POINT_X': '' if cx is None else f'{cx:.4f}',
                'POINT_Y': '' if cy is None else f'{cy:.4f}',
            }
            if cx is not None:
                n_xy += 1
            w.writerow(row)
            n += 1
    print(f'Fairfield parcels written: {n} | residential dwellings (LUC in DWELLING): {n_res} | with centroid: {n_xy}')
    print(f'-> {OUT}')


if __name__ == '__main__':
    main()
