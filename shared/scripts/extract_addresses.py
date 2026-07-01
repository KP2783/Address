#!/usr/bin/env python3
"""
Address Extractor Script
Extracts addresses from OpenAddresses open-source database
Filters by state and zip code
"""

import requests
import json
import csv
import argparse
from typing import List, Dict, Optional
from pathlib import Path
import sys


class AddressExtractor:
    """Extract addresses from OpenAddresses data sources"""

    # OpenAddresses data sources (these are sample URLs - adjust based on actual data availability)
    OPENADDRESSES_API = "https://batch.openaddresses.io/latest/run.json"

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'AddressExtractor/1.0'
        })

    def get_available_datasets(self) -> List[Dict]:
        """Fetch list of available OpenAddresses datasets"""
        try:
            print("Fetching available datasets from OpenAddresses...")
            response = self.session.get(self.OPENADDRESSES_API, timeout=30)
            response.raise_for_status()
            data = response.json()
            return data.get('runs', [])
        except requests.RequestException as e:
            print(f"Error fetching datasets: {e}")
            return []

    def find_dataset_by_state(self, datasets: List[Dict], state: str) -> Optional[Dict]:
        """Find dataset for a specific state"""
        state_lower = state.lower()

        for dataset in datasets:
            source_data = dataset.get('source_data', {})
            # Check if this dataset is for the requested state
            if state_lower in source_data.get('name', '').lower():
                return dataset

        return None

    def download_addresses(self, dataset_url: str, output_file: str) -> bool:
        """Download address data from a dataset URL"""
        try:
            print(f"Downloading addresses from: {dataset_url}")
            response = self.session.get(dataset_url, stream=True, timeout=60)
            response.raise_for_status()

            with open(output_file, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            print(f"Downloaded successfully to: {output_file}")
            return True
        except requests.RequestException as e:
            print(f"Error downloading addresses: {e}")
            return False

    def filter_by_zip(self, input_file: str, zip_codes: List[str], output_file: str) -> int:
        """Filter addresses by zip code(s)"""
        try:
            import pandas as pd

            print(f"Reading address data from: {input_file}")

            # Try to read as CSV (most common format for OpenAddresses)
            try:
                df = pd.read_csv(input_file, low_memory=False)
            except Exception as e:
                print(f"Error reading CSV: {e}")
                return 0

            # Common column names for zip codes in address datasets
            zip_columns = ['postcode', 'zipcode', 'zip', 'postal_code', 'POSTCODE', 'ZIPCODE']
            zip_col = None

            for col in zip_columns:
                if col in df.columns:
                    zip_col = col
                    break

            if not zip_col:
                print(f"Warning: Could not find zip code column. Available columns: {list(df.columns)}")
                # Save all data if no zip column found
                df.to_csv(output_file, index=False)
                return len(df)

            print(f"Found zip code column: {zip_col}")

            # Convert zip codes to strings for comparison
            df[zip_col] = df[zip_col].astype(str)
            zip_codes_str = [str(z) for z in zip_codes]

            # Filter by zip codes
            if zip_codes and zip_codes[0] != 'all':
                filtered_df = df[df[zip_col].isin(zip_codes_str)]
                print(f"Filtered {len(df)} addresses down to {len(filtered_df)} matching zip codes: {', '.join(zip_codes_str)}")
            else:
                filtered_df = df
                print(f"No zip code filter applied. Total addresses: {len(filtered_df)}")

            # Save filtered results
            filtered_df.to_csv(output_file, index=False)
            print(f"Saved filtered addresses to: {output_file}")

            return len(filtered_df)

        except ImportError:
            print("Error: pandas is required. Install with: pip install pandas")
            return 0
        except Exception as e:
            print(f"Error filtering addresses: {e}")
            return 0


def main():
    parser = argparse.ArgumentParser(
        description='Extract addresses from OpenAddresses by state and zip code',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Extract addresses for California, all zip codes
  python extract_addresses.py --state CA --zip all

  # Extract addresses for specific zip codes in California
  python extract_addresses.py --state CA --zip 94102 94103 94104

  # Provide direct CSV file to filter
  python extract_addresses.py --input addresses.csv --zip 10001 10002 --output filtered.csv
        '''
    )

    parser.add_argument('--state', '-s', type=str,
                        help='State code (e.g., CA, NY, TX)')
    parser.add_argument('--zip', '-z', nargs='+', required=True,
                        help='Zip code(s) to filter, or "all" for all zip codes')
    parser.add_argument('--input', '-i', type=str,
                        help='Input CSV file (if you already have address data)')
    parser.add_argument('--output', '-o', type=str,
                        help='Output CSV file (default: addresses_filtered.csv)')
    parser.add_argument('--download-only', action='store_true',
                        help='Only download the dataset without filtering')

    args = parser.parse_args()

    # Set default output file
    if not args.output:
        if args.state:
            args.output = f"addresses_{args.state.lower()}_filtered.csv"
        else:
            args.output = "addresses_filtered.csv"

    extractor = AddressExtractor()

    # If input file is provided, skip download and go straight to filtering
    if args.input:
        if not Path(args.input).exists():
            print(f"Error: Input file not found: {args.input}")
            sys.exit(1)

        count = extractor.filter_by_zip(args.input, args.zip, args.output)
        print(f"\n✓ Success! Extracted {count} addresses to {args.output}")
        return

    # Otherwise, need state to download from OpenAddresses
    if not args.state:
        print("Error: Either --state or --input must be provided")
        parser.print_help()
        sys.exit(1)

    print(f"\n{'='*60}")
    print(f"Address Extraction Tool")
    print(f"{'='*60}")
    print(f"State: {args.state}")
    print(f"Zip Codes: {', '.join(args.zip)}")
    print(f"Output File: {args.output}")
    print(f"{'='*60}\n")

    # Get available datasets
    datasets = extractor.get_available_datasets()

    if not datasets:
        print("\nNote: Could not fetch from OpenAddresses API.")
        print("\nAlternative approaches:")
        print("1. Download address data manually from https://openaddresses.io/")
        print("2. Use the --input flag with a CSV file you already have")
        print(f"\nExample: python extract_addresses.py --input addresses.csv --zip {' '.join(args.zip)} --output {args.output}")
        sys.exit(1)

    # Find dataset for the requested state
    dataset = extractor.find_dataset_by_state(datasets, args.state)

    if not dataset:
        print(f"Could not find dataset for state: {args.state}")
        print("\nAvailable datasets:")
        for ds in datasets[:10]:  # Show first 10
            print(f"  - {ds.get('source_data', {}).get('name', 'Unknown')}")
        sys.exit(1)

    # Download the dataset
    temp_file = f"temp_{args.state.lower()}_addresses.csv"
    output_url = dataset.get('output', {}).get('output', '')

    if not output_url:
        print("Error: No output URL found in dataset")
        sys.exit(1)

    if not extractor.download_addresses(output_url, temp_file):
        sys.exit(1)

    if args.download_only:
        print(f"\n✓ Downloaded to {temp_file}")
        return

    # Filter by zip code
    count = extractor.filter_by_zip(temp_file, args.zip, args.output)

    if count > 0:
        print(f"\n✓ Success! Extracted {count} addresses to {args.output}")

        # Clean up temp file
        try:
            Path(temp_file).unlink()
        except:
            pass
    else:
        print("\n✗ No addresses extracted")
        sys.exit(1)


if __name__ == "__main__":
    main()
