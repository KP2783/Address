#!/usr/bin/env python3
"""
Ohio Address Data Downloader
Downloads address data from ArcGIS REST API services for Ohio
"""

import requests
import json
import csv
import sys
from typing import List, Dict
import time


class OhioAddressDownloader:
    """Download Ohio address data from ArcGIS REST API"""

    # Known Ohio address data sources
    OHIO_SERVICES = [
        {
            "name": "Central Ohio Address Points (OGRIP)",
            "url": "https://services1.arcgis.com/vRyfa9IS9DHj2L0w/arcgis/rest/services/Address_Points/FeatureServer/0",
            "coverage": "Central Ohio"
        },
        {
            "name": "Columbus Address Points",
            "url": "https://services1.arcgis.com/vRyfa9IS9DHj2L0w/arcgis/rest/services/AddressPoints/FeatureServer/0",
            "coverage": "Columbus Metro"
        },
        # Add more county services as needed
    ]

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'OhioAddressDownloader/1.0'
        })

    def query_feature_service(self, service_url: str, where_clause: str = "1=1",
                             offset: int = 0, limit: int = 1000) -> Dict:
        """Query an ArcGIS Feature Service"""
        params = {
            'where': where_clause,
            'outFields': '*',
            'returnGeometry': 'true',
            'f': 'json',
            'resultOffset': offset,
            'resultRecordCount': limit
        }

        try:
            response = self.session.get(
                f"{service_url}/query",
                params=params,
                timeout=60
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error querying service: {e}")
            return {}

    def get_feature_count(self, service_url: str, where_clause: str = "1=1") -> int:
        """Get total count of features"""
        params = {
            'where': where_clause,
            'returnCountOnly': 'true',
            'f': 'json'
        }

        try:
            response = self.session.get(
                f"{service_url}/query",
                params=params,
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            return data.get('count', 0)
        except:
            return 0

    def download_all_features(self, service_url: str, output_file: str,
                             where_clause: str = "1=1", batch_size: int = 1000):
        """Download all features from a service"""
        print(f"Connecting to service...")
        print(f"URL: {service_url}")

        # Get total count
        total_count = self.get_feature_count(service_url, where_clause)
        print(f"Total features: {total_count:,}")

        if total_count == 0:
            print("No features found")
            return 0

        all_features = []
        offset = 0

        print(f"Downloading in batches of {batch_size}...")

        while offset < total_count:
            print(f"Fetching records {offset:,} to {min(offset + batch_size, total_count):,}...")

            result = self.query_feature_service(service_url, where_clause, offset, batch_size)

            if 'features' in result:
                features = result['features']
                if not features:
                    break

                all_features.extend(features)
                offset += len(features)

                # Rate limiting
                time.sleep(0.5)
            else:
                if 'error' in result:
                    print(f"API Error: {result['error']}")
                break

        print(f"\nDownloaded {len(all_features):,} features")

        # Convert to CSV
        if all_features:
            self.save_to_csv(all_features, output_file)
            return len(all_features)

        return 0

    def save_to_csv(self, features: List[Dict], output_file: str):
        """Save features to CSV file"""
        if not features:
            return

        print(f"Converting to CSV...")

        # Extract fields from first feature
        first_feature = features[0]
        attributes = first_feature.get('attributes', {})
        geometry = first_feature.get('geometry', {})

        # Prepare CSV headers
        headers = list(attributes.keys())
        if geometry:
            if 'x' in geometry:
                headers.extend(['longitude', 'latitude'])
            elif 'rings' in geometry or 'paths' in geometry:
                headers.extend(['geometry_json'])

        # Write CSV
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()

            for feature in features:
                row = feature.get('attributes', {}).copy()

                # Add geometry
                geom = feature.get('geometry', {})
                if 'x' in geom:
                    row['longitude'] = geom.get('x')
                    row['latitude'] = geom.get('y')
                elif geom:
                    row['geometry_json'] = json.dumps(geom)

                writer.writerow(row)

        print(f"Saved to: {output_file}")

    def list_available_services(self):
        """List all available Ohio address services"""
        print("\nAvailable Ohio Address Data Sources:")
        print("=" * 70)

        for i, service in enumerate(self.OHIO_SERVICES, 1):
            print(f"\n{i}. {service['name']}")
            print(f"   Coverage: {service['coverage']}")
            print(f"   URL: {service['url']}")

            # Try to get record count
            count = self.get_feature_count(service['url'])
            if count > 0:
                print(f"   Records: {count:,}")

        print("\n" + "=" * 70)


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description='Download Ohio address data from ArcGIS REST services',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # List available data sources
  python download_ohio_addresses.py --list

  # Download from a specific service URL
  python download_ohio_addresses.py --url "https://services1.arcgis.com/.../FeatureServer/0" --output ohio_addresses.csv

  # Download with a filter (e.g., specific zip code)
  python download_ohio_addresses.py --url "..." --where "ZIPCODE='43215'" --output columbus_43215.csv

  # Download from predefined service (by number from --list)
  python download_ohio_addresses.py --service 1 --output central_ohio.csv
        '''
    )

    parser.add_argument('--list', '-l', action='store_true',
                        help='List available Ohio address data sources')
    parser.add_argument('--service', '-s', type=int,
                        help='Download from predefined service (number from --list)')
    parser.add_argument('--url', '-u', type=str,
                        help='ArcGIS FeatureServer URL')
    parser.add_argument('--where', '-w', type=str, default='1=1',
                        help='SQL where clause for filtering (default: "1=1")')
    parser.add_argument('--output', '-o', type=str, default='ohio_addresses.csv',
                        help='Output CSV file')
    parser.add_argument('--batch-size', '-b', type=int, default=1000,
                        help='Batch size for downloads (default: 1000)')

    args = parser.parse_args()

    downloader = OhioAddressDownloader()

    if args.list:
        downloader.list_available_services()
        return

    # Determine service URL
    service_url = None

    if args.service:
        if 1 <= args.service <= len(downloader.OHIO_SERVICES):
            service = downloader.OHIO_SERVICES[args.service - 1]
            service_url = service['url']
            print(f"Selected: {service['name']}")
        else:
            print(f"Error: Service number must be between 1 and {len(downloader.OHIO_SERVICES)}")
            sys.exit(1)
    elif args.url:
        service_url = args.url
    else:
        print("Error: Either --service or --url must be provided")
        print("Use --list to see available services")
        sys.exit(1)

    # Download data
    print(f"\nStarting download...")
    print(f"Output file: {args.output}")
    print(f"Filter: {args.where}")
    print()

    count = downloader.download_all_features(
        service_url,
        args.output,
        args.where,
        args.batch_size
    )

    if count > 0:
        print(f"\n✓ Success! Downloaded {count:,} addresses to {args.output}")
    else:
        print("\n✗ No data downloaded")
        sys.exit(1)


if __name__ == "__main__":
    main()
