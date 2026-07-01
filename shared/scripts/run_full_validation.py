#!/usr/bin/env python3
"""
Run full validation on addresses_43204.csv
This will validate all addresses using the US Census Geocoder API
"""

import csv
import time
import json
import urllib.request
import urllib.parse
import urllib.error
from typing import Dict, List, Tuple
import sys
from datetime import datetime

class AddressValidator:
    def __init__(self):
        self.census_api_url = "https://geocoding.geo.census.gov/geocoder/locations/onelineaddress"
        self.validated_count = 0
        self.invalid_count = 0
        self.errors = []
        self.api_errors = []

    def format_address_for_census(self, row: Dict) -> str:
        """Format address for Census API"""
        parts = []
        if row.get('number'):
            parts.append(row['number'])
        if row.get('street'):
            parts.append(row['street'])
        if row.get('unit'):
            parts.append(row['unit'])
        if row.get('city'):
            parts.append(row['city'])
        if row.get('region'):
            parts.append(row['region'])
        if row.get('postcode'):
            parts.append(row['postcode'])

        return ', '.join(parts)

    def validate_with_census_api(self, address: str) -> Tuple[bool, Dict]:
        """
        Validate address using US Census Geocoder API
        Returns: (is_valid, result_data)
        """
        try:
            params = {
                'address': address,
                'benchmark': 'Public_AR_Current',
                'format': 'json'
            }

            url = f"{self.census_api_url}?{urllib.parse.urlencode(params)}"

            with urllib.request.urlopen(url, timeout=10) as response:
                data = json.loads(response.read().decode())

                if 'result' in data and 'addressMatches' in data['result']:
                    matches = data['result']['addressMatches']
                    if matches:
                        # Address was found and matched
                        match = matches[0]
                        return True, {
                            'matched_address': match.get('matchedAddress', ''),
                            'coordinates': match.get('coordinates', {}),
                            'tiger_line': match.get('tigerLine', {}),
                            'match_type': 'Census Geocoder Match'
                        }
                    else:
                        return False, {'error': 'No matches found'}
                else:
                    return False, {'error': 'Invalid API response'}

        except urllib.error.URLError as e:
            self.api_errors.append(f'Network error: {str(e)}')
            return False, {'error': f'Network error: {str(e)}'}
        except Exception as e:
            self.api_errors.append(f'Validation error: {str(e)}')
            return False, {'error': f'Validation error: {str(e)}'}

    def validate_format(self, row: Dict) -> Tuple[bool, List[str]]:
        """
        Basic format validation
        Returns: (is_valid, list_of_issues)
        """
        issues = []

        # Check required fields
        if not row.get('number') or not row['number'].strip():
            issues.append('Missing house number')

        if not row.get('street') or not row['street'].strip():
            issues.append('Missing street name')

        if not row.get('city') or not row['city'].strip():
            issues.append('Missing city')

        if not row.get('postcode') or not row['postcode'].strip():
            issues.append('Missing zip code')
        else:
            # Validate zip code format
            zipcode = row['postcode'].strip()
            if not zipcode.isdigit() or len(zipcode) != 5:
                issues.append(f'Invalid zip code format: {zipcode}')

            # Check if zip code matches 43204
            if zipcode != '43204':
                issues.append(f'Zip code mismatch: expected 43204, got {zipcode}')

        # Check state
        if row.get('region', '').upper() != 'OH':
            issues.append(f"Invalid state: {row.get('region', 'missing')}")

        return len(issues) == 0, issues

    def validate_address_row(self, row: Dict, use_api: bool = True) -> Dict:
        """
        Validate a single address row
        Returns validation result dictionary
        """
        result = {
            'original_address': self.format_address_for_census(row),
            'format_valid': False,
            'api_valid': False,
            'format_issues': [],
            'api_result': {}
        }

        # First, validate format
        format_valid, format_issues = self.validate_format(row)
        result['format_valid'] = format_valid
        result['format_issues'] = format_issues

        # If format is valid and API validation is requested
        if format_valid and use_api:
            address = self.format_address_for_census(row)
            api_valid, api_data = self.validate_with_census_api(address)
            result['api_valid'] = api_valid
            result['api_result'] = api_data

        return result

    def run_full_validation(self):
        """Run full validation on addresses_43204.csv"""

        input_file = 'addresses_43204.csv'
        output_file = 'validation_results_full.json'

        print("=" * 80)
        print("FULL ADDRESS VALIDATION")
        print("=" * 80)
        print(f"Input file: {input_file}")
        print(f"Output file: {output_file}")
        print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        print("\nThis will validate ALL addresses using the US Census Geocoder API")
        print("Estimated time: 1-2 hours for ~23,000 addresses")
        print("\nProgress will be shown every 100 addresses...")
        print("-" * 80)

        results = []
        start_time = time.time()

        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)

                for i, row in enumerate(reader, 1):
                    # Validate the address
                    result = self.validate_address_row(row, use_api=True)
                    results.append(result)

                    # Track stats
                    if result['format_valid']:
                        if result['api_valid']:
                            self.validated_count += 1
                            status = "✓"
                        else:
                            self.invalid_count += 1
                            status = "✗"
                            self.errors.append({
                                'address': result['original_address'],
                                'reason': result['api_result'].get('error', 'Not found')
                            })
                    else:
                        self.invalid_count += 1
                        status = "✗"
                        self.errors.append({
                            'address': result['original_address'],
                            'reason': ', '.join(result['format_issues'])
                        })

                    # Print progress every 100 addresses
                    if i % 100 == 0:
                        elapsed = time.time() - start_time
                        rate = i / elapsed
                        remaining = (23073 - i) / rate if rate > 0 else 0

                        print(f"[{i:5d}] Valid: {self.validated_count:5d} | Invalid: {self.invalid_count:3d} | "
                              f"Rate: {rate:.1f}/s | ETA: {remaining/60:.0f}min")

                    # Show first 20 in detail
                    elif i <= 20:
                        addr_short = result['original_address'][:50]
                        print(f"[{i:5d}] {status} {addr_short}")
                        if result.get('api_valid') and result['api_result'].get('matched_address'):
                            print(f"        Matched: {result['api_result']['matched_address']}")

                    # Delay to avoid rate limiting
                    time.sleep(0.2)

                    # Save intermediate results every 1000 addresses
                    if i % 1000 == 0:
                        self.save_intermediate_results(results, f'validation_results_intermediate_{i}.json')

            # Write final results
            print(f"\n\nWriting final results to {output_file}...")
            self.write_results(results, output_file)

            # Print summary
            self.print_summary(start_time)

        except FileNotFoundError:
            print(f"Error: File '{input_file}' not found")
            sys.exit(1)
        except KeyboardInterrupt:
            print(f"\n\n⚠️  Validation interrupted by user")
            print(f"Saving partial results...")
            self.write_results(results, 'validation_results_partial.json')
            self.print_summary(start_time)
            sys.exit(0)
        except Exception as e:
            print(f"Error during validation: {e}")
            print(f"Saving partial results...")
            self.write_results(results, 'validation_results_error.json')
            sys.exit(1)

    def save_intermediate_results(self, results: List[Dict], filename: str):
        """Save intermediate results"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump({
                'total_checked': len(results),
                'valid_count': self.validated_count,
                'invalid_count': self.invalid_count,
                'partial': True
            }, f, indent=2)

    def write_results(self, results: List[Dict], output_file: str):
        """Write validation results to JSON file"""
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({
                'total_checked': len(results),
                'valid_count': self.validated_count,
                'invalid_count': self.invalid_count,
                'validation_rate': f"{(self.validated_count / len(results) * 100):.2f}%" if results else "0%",
                'results': results,
                'errors': self.errors[:100],  # Only save first 100 errors to keep file size reasonable
                'api_errors_count': len(self.api_errors),
                'total_errors_count': len(self.errors)
            }, f, indent=2)

    def print_summary(self, start_time):
        """Print validation summary"""
        total = self.validated_count + self.invalid_count
        elapsed = time.time() - start_time

        print("\n" + "=" * 80)
        print("VALIDATION SUMMARY")
        print("=" * 80)
        print(f"Total addresses checked: {total:,}")
        print(f"✓ Valid addresses: {self.validated_count:,} ({self.validated_count/total*100:.2f}%)")
        print(f"✗ Invalid addresses: {self.invalid_count:,} ({self.invalid_count/total*100:.2f}%)")
        print(f"\nTotal time: {elapsed/60:.1f} minutes ({elapsed/3600:.2f} hours)")
        print(f"Average rate: {total/elapsed:.1f} addresses/second")
        print("=" * 80)

        if self.errors:
            print(f"\nTotal errors found: {len(self.errors)}")
            print("\nFirst 10 errors:")
            for i, error in enumerate(self.errors[:10], 1):
                print(f"{i}. {error['address']}")
                print(f"   Reason: {error['reason']}")


if __name__ == '__main__':
    validator = AddressValidator()
    validator.run_full_validation()
