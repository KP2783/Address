#!/usr/bin/env python3
"""
Download Ohio addresses from OpenStreetMap using Overpass API
"""

import requests
import json
import csv
import time
import sys
from typing import List, Dict


class OSMAddressDownloader:
    """Download address data from OpenStreetMap"""

    OVERPASS_API = "https://overpass-api.de/api/interpreter"

    # Ohio bounding box [south, west, north, east]
    OHIO_BBOX = [38.4031, -84.8203, 42.3233, -80.5190]

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'OhioAddressDownloader/1.0'
        })

    def build_overpass_query(self, bbox: List[float] = None, limit: int = None) -> str:
        """Build Overpass QL query for addresses"""
        if bbox is None:
            bbox = self.OHIO_BBOX

        # bbox format: south, west, north, east
        bbox_str = f"{bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]}"

        query = f"""
        [out:json][timeout:300];
        (
          node["addr:housenumber"]["addr:street"]({bbox_str});
          way["addr:housenumber"]["addr:street"]({bbox_str});
        );
        out center;
        """

        return query

    def query_overpass(self, query: str) -> Dict:
        """Query Overpass API"""
        try:
            print("Querying OpenStreetMap...")
            print("This may take several minutes for large areas...")

            response = self.session.post(
                self.OVERPASS_API,
                data={'data': query},
                timeout=600
            )
            response.raise_for_status()
            return response.json()

        except requests.Timeout:
            print("Query timed out. Try a smaller area or use bbox parameter.")
            return {}
        except requests.RequestException as e:
            print(f"Error querying Overpass API: {e}")
            return {}

    def download_ohio_addresses(self, output_file: str, bbox: List[float] = None):
        """Download Ohio addresses from OSM"""
        query = self.build_overpass_query(bbox)

        data = self.query_overpass(query)

        if not data or 'elements' not in data:
            print("No data returned")
            return 0

        elements = data['elements']
        print(f"Retrieved {len(elements)} address points from OpenStreetMap")

        # Convert to address records
        addresses = []

        for element in elements:
            tags = element.get('tags', {})

            # Get coordinates
            if element['type'] == 'node':
                lat = element.get('lat')
                lon = element.get('lon')
            elif 'center' in element:
                lat = element['center'].get('lat')
                lon = element['center'].get('lon')
            else:
                continue

            # Build address record
            address = {
                'housenumber': tags.get('addr:housenumber', ''),
                'street': tags.get('addr:street', ''),
                'city': tags.get('addr:city', ''),
                'postcode': tags.get('addr:postcode', ''),
                'state': tags.get('addr:state', 'OH'),
                'latitude': lat,
                'longitude': lon,
                'osm_id': element.get('id', ''),
                'osm_type': element.get('type', '')
            }

            addresses.append(address)

        # Save to CSV
        if addresses:
            self.save_to_csv(addresses, output_file)
            return len(addresses)

        return 0

    def download_by_city(self, city_name: str, output_file: str):
        """Download addresses for a specific Ohio city"""
        # Simplified bounding boxes for major Ohio cities
        city_bboxes = {
            'columbus': [39.8847, -83.1532, 40.1409, -82.8837],
            'cleveland': [41.3912, -81.8760, 41.6054, -81.5397],
            'cincinnati': [39.0511, -84.7411, 39.1986, -84.3877],
            'toledo': [41.6087, -83.7221, 41.7322, -83.4082],
            'akron': [41.0288, -81.6136, 41.1435, -81.4216],
            'dayton': [39.7009, -84.2606, 39.8250, -84.1178]
        }

        city_lower = city_name.lower()
        if city_lower not in city_bboxes:
            print(f"City '{city_name}' not found in predefined cities")
            print(f"Available cities: {', '.join(city_bboxes.keys())}")
            return 0

        print(f"Downloading addresses for {city_name.title()}, Ohio...")
        return self.download_ohio_addresses(output_file, city_bboxes[city_lower])

    def save_to_csv(self, addresses: List[Dict], output_file: str):
        """Save addresses to CSV"""
        if not addresses:
            return

        print(f"Saving {len(addresses)} addresses to CSV...")

        fields = ['housenumber', 'street', 'city', 'state', 'postcode',
                 'latitude', 'longitude', 'osm_id', 'osm_type']

        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            writer.writerows(addresses)

        print(f"Saved to: {output_file}")


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description='Download Ohio addresses from OpenStreetMap',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Download addresses for a specific city
  python download_osm_ohio_addresses.py --city Columbus --output columbus_addresses.csv

  # Download addresses for a custom bounding box
  python download_osm_ohio_addresses.py --bbox 39.9 -83.1 40.1 -82.9 --output custom_area.csv

  # Available cities: Columbus, Cleveland, Cincinnati, Toledo, Akron, Dayton

Note: OpenStreetMap data coverage varies by area. Some areas may have incomplete address data.
The Overpass API has rate limits and may timeout for very large queries.
        '''
    )

    parser.add_argument('--city', '-c', type=str,
                        help='Ohio city name (Columbus, Cleveland, Cincinnati, etc.)')
    parser.add_argument('--bbox', '-b', nargs=4, type=float, metavar=('SOUTH', 'WEST', 'NORTH', 'EAST'),
                        help='Custom bounding box (south west north east)')
    parser.add_argument('--output', '-o', type=str, default='ohio_osm_addresses.csv',
                        help='Output CSV file')
    parser.add_argument('--statewide', action='store_true',
                        help='Download entire state (WARNING: May timeout or take very long)')

    args = parser.parse_args()

    downloader = OSMAddressDownloader()

    if args.city:
        count = downloader.download_by_city(args.city, args.output)
    elif args.bbox:
        count = downloader.download_ohio_addresses(args.output, args.bbox)
    elif args.statewide:
        print("WARNING: Downloading entire state from OSM may timeout")
        print("Consider downloading by city or county instead")
        response = input("Continue? (y/n): ")
        if response.lower() != 'y':
            sys.exit(0)
        count = downloader.download_ohio_addresses(args.output)
    else:
        print("Error: Must specify --city, --bbox, or --statewide")
        parser.print_help()
        sys.exit(1)

    if count > 0:
        print(f"\n✓ Success! Downloaded {count:,} addresses to {args.output}")
    else:
        print("\n✗ No addresses downloaded")
        sys.exit(1)


if __name__ == "__main__":
    main()
