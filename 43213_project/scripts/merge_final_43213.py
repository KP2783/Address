#!/usr/bin/env python3
"""
Merge Google validation results with county parcel data for 43213.
Classification priority:
  1. Google API result (most accurate for residential vs commercial)
  2. Parcel land use code (for addresses not Google-validated)
  3. Default to residential for unmatched apartment units
Outputs residential-only addresses with all enrichment data.
"""

import csv
import re

ENRICHED_FILE = '/Users/kevinpatel/Address/43213_project/data/addresses_43213_enriched.csv'
GOOGLE_FILE = '/Users/kevinpatel/Address/43213_project/output/google_validation_results.csv'
OUTPUT_ALL = '/Users/kevinpatel/Address/43213_project/data/addresses_43213_final.csv'
OUTPUT_RES = '/Users/kevinpatel/Address/43213_project/data/addresses_43213_residential_final.csv'
OUTPUT_FMT = '/Users/kevinpatel/Address/43213_project/data/addresses_43213_formatted.csv'

RESIDENTIAL_LAND_USE = {
    '500', '501', '503', '510', '511', '520', '530',
    '550', '551', '552', '553', '559', '560',
}

# Land use codes that are apartment complexes classified as commercial
APT_COMPLEX_LAND_USE = {'401'}

OUTPUT_FIELDS = [
    'address', 'number', 'street', 'unit', 'city', 'state', 'zip',
    'latitude', 'longitude',
    'final_classification', 'classification_source',
    'google_validated_address', 'google_classification', 'google_city',
    'parcel_id', 'land_use_code', 'land_use_type', 'occupancy',
    'owner_name', 'homestead', 'year_built', 'bedrooms', 'bathrooms',
    'appraised_value', 'annual_tax', 'sale_price', 'sale_date',
]


def build_addr_key(row):
    street = re.sub(r'\s+', ' ', row['street']).strip()
    unit_part = f" {row['unit']}" if row.get('unit') else ''
    city = row['city'] if row.get('city') else 'Columbus'
    return f"{row['number']} {street}{unit_part}, {city}, OH, 43213"


def main():
    # Load Google results
    google = {}
    with open(GOOGLE_FILE) as f:
        reader = csv.DictReader(f)
        for row in reader:
            google[row['address']] = row
    print(f"Google results loaded: {len(google)}")

    # Process enriched data and merge
    results = []
    stats = {
        'google_residential': 0, 'google_commercial': 0,
        'parcel_residential': 0, 'parcel_commercial': 0,
        'parcel_apt_complex': 0, 'default_residential': 0,
        'total': 0,
    }

    with open(ENRICHED_FILE) as f:
        reader = csv.DictReader(f)
        for row in reader:
            stats['total'] += 1
            key = build_addr_key(row)
            g = google.get(key, {})

            out = {
                'address': key,
                'number': row['number'],
                'street': re.sub(r'\s+', ' ', row['street']).strip(),
                'unit': row.get('unit', ''),
                'city': row.get('city', '') or 'Columbus',
                'state': 'OH',
                'zip': '43213',
                'latitude': row.get('latitude', ''),
                'longitude': row.get('longitude', ''),
                'parcel_id': row.get('parcel_id', ''),
                'land_use_code': row.get('land_use_code', ''),
                'land_use_type': row.get('land_use_type', ''),
                'occupancy': row.get('occupancy', ''),
                'owner_name': row.get('owner_name', ''),
                'homestead': row.get('homestead', ''),
                'year_built': row.get('year_built', ''),
                'bedrooms': row.get('bedrooms', ''),
                'bathrooms': row.get('bathrooms', ''),
                'appraised_value': row.get('appraised_value', ''),
                'annual_tax': row.get('annual_tax', ''),
                'sale_price': row.get('sale_price', ''),
                'sale_date': row.get('sale_date', ''),
                'google_validated_address': g.get('validated_address', ''),
                'google_classification': g.get('classification', ''),
                'google_city': g.get('city', ''),
            }

            # Classification priority
            if g:
                # Google validated - trust it
                out['final_classification'] = g['classification']
                out['classification_source'] = 'google_api'
                if g['classification'] == 'RESIDENTIAL':
                    stats['google_residential'] += 1
                else:
                    stats['google_commercial'] += 1
                # Use Google's city if available
                if g.get('city'):
                    out['city'] = g['city']
            elif row['match_status'] == 'MATCHED':
                lu = row.get('land_use_code', '')
                if lu in RESIDENTIAL_LAND_USE:
                    out['final_classification'] = 'RESIDENTIAL'
                    out['classification_source'] = 'parcel_land_use'
                    stats['parcel_residential'] += 1
                elif lu in APT_COMPLEX_LAND_USE:
                    # Apt complexes on commercial parcels - Google showed these are residential
                    out['final_classification'] = 'RESIDENTIAL'
                    out['classification_source'] = 'parcel_apt_complex'
                    stats['parcel_apt_complex'] += 1
                else:
                    out['final_classification'] = 'COMMERCIAL'
                    out['classification_source'] = 'parcel_land_use'
                    stats['parcel_commercial'] += 1
            else:
                # Unmatched - most are apartment units, default residential
                out['final_classification'] = 'RESIDENTIAL'
                out['classification_source'] = 'default_unmatched'
                stats['default_residential'] += 1

            results.append(out)

    # Write all results
    with open(OUTPUT_ALL, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=OUTPUT_FIELDS)
        writer.writeheader()
        writer.writerows(results)

    # Write residential only
    residential = [r for r in results if r['final_classification'] == 'RESIDENTIAL']
    with open(OUTPUT_RES, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=OUTPUT_FIELDS)
        writer.writeheader()
        writer.writerows(residential)

    # Write formatted addresses (residential only)
    with open(OUTPUT_FMT, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['address'])
        for r in residential:
            writer.writerow([r['address']])

    print(f"\n=== Final Classification Summary ===")
    print(f"Total addresses: {stats['total']}")
    print(f"\nClassification breakdown:")
    print(f"  Google -> RESIDENTIAL: {stats['google_residential']}")
    print(f"  Google -> COMMERCIAL:  {stats['google_commercial']}")
    print(f"  Parcel -> RESIDENTIAL: {stats['parcel_residential']}")
    print(f"  Parcel -> COMMERCIAL:  {stats['parcel_commercial']}")
    print(f"  Parcel apt complex -> RESIDENTIAL: {stats['parcel_apt_complex']}")
    print(f"  Default unmatched -> RESIDENTIAL: {stats['default_residential']}")

    total_res = stats['google_residential'] + stats['parcel_residential'] + stats['parcel_apt_complex'] + stats['default_residential']
    total_comm = stats['google_commercial'] + stats['parcel_commercial']
    print(f"\nFinal:")
    print(f"  RESIDENTIAL: {total_res}")
    print(f"  COMMERCIAL:  {total_comm}")
    print(f"\nFiles written:")
    print(f"  All: {OUTPUT_ALL}")
    print(f"  Residential only: {OUTPUT_RES}")
    print(f"  Formatted: {OUTPUT_FMT}")


if __name__ == '__main__':
    main()
