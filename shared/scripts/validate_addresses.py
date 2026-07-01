#!/usr/bin/env python3
"""
Address Validation Script
Validates addresses from CSV file using multiple methods:
1. US Census Geocoder (free, no API key)
2. Format validation
3. Zip code validation
4. Basic deliverability checks
"""

import csv
import time
import json
import urllib.request
import urllib.parse
import urllib.error
from typing import Dict, List, Tuple
import sys

class AddressValidator:
    def __init__(self):
        self.census_api_url = "https://geocoding.geo.census.gov/geocoder/locations/onelineaddress"
        self.validated_count = 0
        self.invalid_count = 0
        self.errors = []

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
            return False, {'error': f'Network error: {str(e)}'}
        except Exception as e:
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

    def validate_csv_file(self, input_file: str, output_file: str,
                         sample_size: int = None, use_api: bool = True,
                         delay: float = 0.2):
        """
        Validate addresses from CSV file

        Args:
            input_file: Path to input CSV
            output_file: Path to output validation results
            sample_size: Number of addresses to validate (None = all)
            use_api: Whether to use Census API validation
            delay: Delay between API calls (seconds)
        """
        print(f"Starting validation of {input_file}")
        print(f"API validation: {'Enabled' if use_api else 'Disabled'}")
        if sample_size:
            print(f"Sample size: {sample_size} addresses")
        print("-" * 80)

        results = []

        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)

                for i, row in enumerate(reader, 1):
                    if sample_size and i > sample_size:
                        break

                    # Validate the address
                    result = self.validate_address_row(row, use_api=use_api)
                    results.append(result)

                    # Print progress
                    if i % 10 == 0:
                        print(f"Processed {i} addresses...", end='\r')

                    # Track stats
                    if result['format_valid']:
                        if use_api:
                            if result['api_valid']:
                                self.validated_count += 1
                                status = "✓ VALID"
                            else:
                                self.invalid_count += 1
                                status = "✗ NOT FOUND"
                                self.errors.append({
                                    'address': result['original_address'],
                                    'reason': result['api_result'].get('error', 'Not found')
                                })
                        else:
                            self.validated_count += 1
                            status = "✓ FORMAT OK"
                    else:
                        self.invalid_count += 1
                        status = "✗ FORMAT ERROR"
                        self.errors.append({
                            'address': result['original_address'],
                            'reason': ', '.join(result['format_issues'])
                        })

                    # Print sample results
                    if i <= 20 or (i % 100 == 0):
                        print(f"\n[{i}] {status}: {result['original_address'][:60]}")
                        if result['format_issues']:
                            print(f"    Issues: {', '.join(result['format_issues'])}")
                        if result.get('api_valid') and result['api_result'].get('matched_address'):
                            print(f"    Matched: {result['api_result']['matched_address']}")

                    # Delay to avoid rate limiting
                    if use_api:
                        time.sleep(delay)

            # Write results to file
            print(f"\n\nWriting results to {output_file}...")
            self.write_results(results, output_file)

            # Print summary
            self.print_summary()

        except FileNotFoundError:
            print(f"Error: File '{input_file}' not found")
            sys.exit(1)
        except Exception as e:
            print(f"Error during validation: {e}")
            sys.exit(1)

    def write_results(self, results: List[Dict], output_file: str):
        """Write validation results to JSON file"""
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({
                'total_checked': len(results),
                'valid_count': self.validated_count,
                'invalid_count': self.invalid_count,
                'validation_rate': f"{(self.validated_count / len(results) * 100):.2f}%" if results else "0%",
                'results': results,
                'errors': self.errors
            }, f, indent=2)

    def print_summary(self):
        """Print validation summary"""
        total = self.validated_count + self.invalid_count
        print("\n" + "=" * 80)
        print("VALIDATION SUMMARY")
        print("=" * 80)
        print(f"Total addresses checked: {total}")
        print(f"✓ Valid addresses: {self.validated_count} ({self.validated_count/total*100:.2f}%)")
        print(f"✗ Invalid addresses: {self.invalid_count} ({self.invalid_count/total*100:.2f}%)")
        print("=" * 80)

        if self.errors and len(self.errors) <= 20:
            print("\nFirst issues found:")
            for i, error in enumerate(self.errors[:20], 1):
                print(f"{i}. {error['address']}")
                print(f"   Reason: {error['reason']}")


def main():
    """Main function with usage examples"""
    validator = AddressValidator()

    print("=" * 80)
    print("ADDRESS VALIDATION TOOL")
    print("=" * 80)
    print("\nThis tool validates addresses using:")
    print("1. Format validation (house number, street, city, zip)")
    print("2. US Census Geocoder API (confirms address exists)")
    print("\n")

    # Get user input
    print("Validation Options:")
    print("1. Quick test (first 50 addresses with API validation)")
    print("2. Format-only validation (fast, all addresses)")
    print("3. Full API validation (slow, all addresses)")
    print("4. Custom sample size")

    choice = input("\nEnter your choice (1-4): ").strip()

    input_file = 'addresses_43204.csv'

    if choice == '1':
        # Quick test with 50 addresses
        output_file = 'validation_results_sample.json'
        validator.validate_csv_file(input_file, output_file, sample_size=50, use_api=True)

    elif choice == '2':
        # Format-only validation (fast)
        output_file = 'validation_results_format_only.json'
        validator.validate_csv_file(input_file, output_file, use_api=False)

    elif choice == '3':
        # Full API validation
        print("\n⚠️  WARNING: This will take a long time!")
        print("Estimated time: ~1-2 hours for 23,000 addresses")
        confirm = input("Continue? (yes/no): ").strip().lower()
        if confirm == 'yes':
            output_file = 'validation_results_full.json'
            validator.validate_csv_file(input_file, output_file, use_api=True)
        else:
            print("Cancelled.")
            return

    elif choice == '4':
        # Custom sample
        sample = int(input("Enter number of addresses to validate: ").strip())
        api = input("Use API validation? (yes/no): ").strip().lower() == 'yes'
        output_file = f'validation_results_{sample}.json'
        validator.validate_csv_file(input_file, output_file, sample_size=sample, use_api=api)

    else:
        print("Invalid choice. Exiting.")
        return

    print(f"\n✓ Results saved to: {output_file}")
    print("\nYou can review the detailed results in the JSON file.")


if __name__ == '__main__':
    main()
