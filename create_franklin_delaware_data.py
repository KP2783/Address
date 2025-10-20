#!/usr/bin/env python3
"""
Generate comprehensive sample address data for Franklin and Delaware Counties, Ohio
"""

import csv
import random

# Franklin County (Columbus metro area)
franklin_data = {
    'county': 'Franklin',
    'cities': {
        'Columbus': {
            'zips': ['43004', '43026', '43054', '43081', '43082', '43085', '43119', '43123',
                    '43201', '43202', '43203', '43204', '43205', '43206', '43207', '43209',
                    '43210', '43211', '43212', '43213', '43214', '43215', '43217', '43219',
                    '43220', '43221', '43222', '43223', '43224', '43227', '43229', '43230',
                    '43231', '43232', '43235'],
            'streets': ['High St', 'Broad St', 'Main St', 'Long St', 'Spring St', 'Gay St',
                       'Rich St', 'Town St', 'State St', 'Park St', 'Summit St', 'Grant Ave',
                       'Cleveland Ave', 'Livingston Ave', 'Morse Rd', 'Bethel Rd', 'Henderson Rd'],
            'lat_base': 39.9612,
            'lon_base': -82.9988,
            'count': 800
        },
        'Westerville': {
            'zips': ['43081', '43082'],
            'streets': ['State St', 'Main St', 'Cleveland Ave', 'Otterbein Ave', 'Home St'],
            'lat_base': 40.1262,
            'lon_base': -82.9291,
            'count': 100
        },
        'Grove City': {
            'zips': ['43123'],
            'streets': ['Broadway', 'Park St', 'Main St', 'Columbus St', 'Franklin St'],
            'lat_base': 39.8814,
            'lon_base': -83.0930,
            'count': 80
        },
        'Gahanna': {
            'zips': ['43230'],
            'streets': ['Granville St', 'Tech Center Dr', 'Hamilton Rd', 'Stygler Rd'],
            'lat_base': 40.0192,
            'lon_base': -82.8796,
            'count': 70
        },
        'Reynoldsburg': {
            'zips': ['43068'],
            'streets': ['Main St', 'Lancaster Ave', 'Brice Rd', 'Taylor Rd'],
            'lat_base': 39.9548,
            'lon_base': -82.8121,
            'count': 60
        }
    }
}

# Delaware County (north of Franklin County)
delaware_data = {
    'county': 'Delaware',
    'cities': {
        'Delaware': {
            'zips': ['43015'],
            'streets': ['Sandusky St', 'Winter St', 'William St', 'Central Ave', 'Lake St',
                       'Union St', 'Franklin St', 'Washington St', 'London Rd'],
            'lat_base': 40.2987,
            'lon_base': -83.0680,
            'count': 200
        },
        'Powell': {
            'zips': ['43065'],
            'streets': ['Sawmill Pkwy', 'Liberty St', 'Olentangy St', 'Village Way'],
            'lat_base': 40.1579,
            'lon_base': -83.0752,
            'count': 120
        },
        'Sunbury': {
            'zips': ['43074'],
            'streets': ['State St', 'Granville St', 'Columbus St', 'Vernon St'],
            'lat_base': 40.2423,
            'lon_base': -82.8590,
            'count': 80
        },
        'Galena': {
            'zips': ['43021'],
            'streets': ['Main St', 'Plumb Rd', 'Big Walnut Rd', 'Dustin Rd'],
            'lat_base': 40.1918,
            'lon_base': -82.8804,
            'count': 50
        },
        'Lewis Center': {
            'zips': ['43035'],
            'streets': ['Polaris Pkwy', 'Orange Rd', 'Shanahan Rd', 'US 23'],
            'lat_base': 40.1987,
            'lon_base': -83.0110,
            'count': 150
        }
    }
}

def generate_addresses(county_data):
    """Generate address records for a county"""
    addresses = []
    county_name = county_data['county']

    for city, data in county_data['cities'].items():
        num_addresses = data['count']

        for i in range(num_addresses):
            zip_code = random.choice(data['zips'])
            street = random.choice(data['streets'])
            number = random.randint(100, 9999)

            # Add variation to coordinates
            lat = data['lat_base'] + random.uniform(-0.08, 0.08)
            lon = data['lon_base'] + random.uniform(-0.08, 0.08)

            addresses.append({
                'number': number,
                'street': street,
                'city': city,
                'county': county_name,
                'state': 'OH',
                'postcode': zip_code,
                'latitude': round(lat, 6),
                'longitude': round(lon, 6)
            })

    return addresses

def main():
    print("Generating Franklin County address data...")
    franklin_addresses = generate_addresses(franklin_data)
    print(f"Generated {len(franklin_addresses)} addresses")

    print("\nGenerating Delaware County address data...")
    delaware_addresses = generate_addresses(delaware_data)
    print(f"Generated {len(delaware_addresses)} addresses")

    # Save Franklin County
    with open('franklin_county_addresses.csv', 'w', newline='') as f:
        fields = ['number', 'street', 'city', 'county', 'state', 'postcode', 'latitude', 'longitude']
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(franklin_addresses)
    print(f"\nSaved Franklin County data to: franklin_county_addresses.csv")

    # Save Delaware County
    with open('delaware_county_addresses.csv', 'w', newline='') as f:
        fields = ['number', 'street', 'city', 'county', 'state', 'postcode', 'latitude', 'longitude']
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(delaware_addresses)
    print(f"Saved Delaware County data to: delaware_county_addresses.csv")

    # Save combined
    combined = franklin_addresses + delaware_addresses
    with open('franklin_delaware_combined.csv', 'w', newline='') as f:
        fields = ['number', 'street', 'city', 'county', 'state', 'postcode', 'latitude', 'longitude']
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(combined)
    print(f"Saved combined data to: franklin_delaware_combined.csv")

    # Print statistics
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print(f"\nFranklin County:")
    print(f"  Total Addresses: {len(franklin_addresses):,}")
    print(f"  Cities: {len(franklin_data['cities'])}")
    print(f"  Unique Zip Codes: {len(set(a['postcode'] for a in franklin_addresses))}")

    print(f"\nDelaware County:")
    print(f"  Total Addresses: {len(delaware_addresses):,}")
    print(f"  Cities: {len(delaware_data['cities'])}")
    print(f"  Unique Zip Codes: {len(set(a['postcode'] for a in delaware_addresses))}")

    print(f"\nCombined:")
    print(f"  Total Addresses: {len(combined):,}")
    print(f"  Total Cities: {len(franklin_data['cities']) + len(delaware_data['cities'])}")
    print(f"  Total Zip Codes: {len(set(a['postcode'] for a in combined))}")
    print("="*70)

if __name__ == "__main__":
    main()
