#!/usr/bin/env python3
"""
Comprehensive Address Validation - Tracks EVERY address
Creates a detailed CSV with validation status for each address
"""

import csv
import time
import json
import urllib.request
import urllib.parse
import urllib.error
from datetime import datetime

class ComprehensiveValidator:
    def __init__(self):
        self.census_api_url = "https://geocoding.geo.census.gov/geocoder/locations/onelineaddress"
        self.results = []
        self.valid_count = 0
        self.invalid_count = 0

    def format_address(self, row):
        """Format address for Census API"""
        parts = []
        if row.get('number'): parts.append(row['number'])
        if row.get('street'): parts.append(row['street'])
        if row.get('unit'): parts.append(row['unit'])
        if row.get('city'): parts.append(row['city'])
        if row.get('region'): parts.append(row['region'])
        if row.get('postcode'): parts.append(row['postcode'])
        return ', '.join(parts)

    def validate_format(self, row):
        """Check if address has proper format"""
        issues = []
        if not row.get('number') or not row['number'].strip():
            issues.append('Missing house number')
        if not row.get('street') or not row['street'].strip():
            issues.append('Missing street name')
        if not row.get('city') or not row['city'].strip():
            issues.append('Missing city')
        if not row.get('postcode') or not row['postcode'].strip():
            issues.append('Missing zip code')
        else:
            zipcode = row['postcode'].strip()
            if not zipcode.isdigit() or len(zipcode) != 5:
                issues.append(f'Invalid zip format: {zipcode}')
            if zipcode != '43204':
                issues.append(f'Wrong zip code: {zipcode}')
        if row.get('region', '').upper() != 'OH':
            issues.append(f"Wrong state: {row.get('region', 'N/A')}")

        return len(issues) == 0, issues

    def validate_with_census(self, address):
        """Validate address with US Census Geocoder"""
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
                        match = matches[0]
                        return True, {
                            'matched_address': match.get('matchedAddress', ''),
                            'coordinates': match.get('coordinates', {}),
                            'tiger_line_id': match.get('tigerLine', {}).get('tigerLineId', '')
                        }
                    else:
                        return False, {'error': 'No match found in Census database'}
                else:
                    return False, {'error': 'Invalid API response'}

        except urllib.error.URLError as e:
            return False, {'error': f'Network error: {str(e)}'}
        except Exception as e:
            return False, {'error': f'API error: {str(e)}'}

    def validate_all(self):
        """Validate all addresses and track each one"""

        input_file = 'addresses_43204.csv'
        output_csv = 'validation_results_detailed.csv'
        output_json = 'validation_results_full.json'

        print("=" * 80)
        print("COMPREHENSIVE ADDRESS VALIDATION")
        print("=" * 80)
        print(f"Input: {input_file}")
        print(f"Output CSV: {output_csv}")
        print(f"Output JSON: {output_json}")
        print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        print("\nValidating ALL 23,073 addresses...")
        print("Each address will be tracked with validation status\n")
        print("-" * 80)

        start_time = time.time()

        # Open output CSV immediately
        with open(output_csv, 'w', newline='', encoding='utf-8') as out_f:
            csv_writer = csv.writer(out_f)
            # Write header
            csv_writer.writerow([
                'row_number', 'original_address', 'validation_status',
                'format_valid', 'census_valid', 'matched_address',
                'latitude', 'longitude', 'error_reason'
            ])

            # Process each address
            with open(input_file, 'r', encoding='utf-8') as in_f:
                reader = csv.DictReader(in_f)

                for i, row in enumerate(reader, 1):
                    original_address = self.format_address(row)

                    # Step 1: Format validation
                    format_valid, format_issues = self.validate_format(row)

                    result = {
                        'row_number': i,
                        'original_address': original_address,
                        'house_number': row.get('number', ''),
                        'street': row.get('street', ''),
                        'city': row.get('city', ''),
                        'format_valid': format_valid,
                        'census_valid': False,
                        'matched_address': '',
                        'latitude': '',
                        'longitude': '',
                        'error_reason': ''
                    }

                    # Step 2: If format valid, check with Census
                    if format_valid:
                        census_valid, census_data = self.validate_with_census(original_address)
                        result['census_valid'] = census_valid

                        if census_valid:
                            result['matched_address'] = census_data.get('matched_address', '')
                            coords = census_data.get('coordinates', {})
                            result['latitude'] = coords.get('y', '')
                            result['longitude'] = coords.get('x', '')
                            result['validation_status'] = 'VALID'
                            self.valid_count += 1
                        else:
                            result['validation_status'] = 'INVALID - Not in Census DB'
                            result['error_reason'] = census_data.get('error', 'Not found')
                            self.invalid_count += 1
                    else:
                        result['validation_status'] = 'INVALID - Format Error'
                        result['error_reason'] = '; '.join(format_issues)
                        self.invalid_count += 1

                    # Store result
                    self.results.append(result)

                    # Write to CSV immediately
                    csv_writer.writerow([
                        result['row_number'],
                        result['original_address'],
                        result['validation_status'],
                        result['format_valid'],
                        result['census_valid'],
                        result['matched_address'],
                        result['latitude'],
                        result['longitude'],
                        result['error_reason']
                    ])

                    # Print progress
                    if i <= 20:
                        status = "✓" if result['validation_status'] == 'VALID' else "✗"
                        print(f"[{i:5d}] {status} {original_address[:50]}")
                        if result['validation_status'] != 'VALID':
                            print(f"        Reason: {result['error_reason']}")
                    elif i % 100 == 0:
                        elapsed = time.time() - start_time
                        rate = i / elapsed if elapsed > 0 else 0
                        remaining = (23073 - i) / rate if rate > 0 else 0

                        print(f"[{i:5d}] Valid: {self.valid_count:5d} | Invalid: {self.invalid_count:3d} | "
                              f"Rate: {rate:.1f}/s | ETA: {remaining/60:.0f}min")

                        # Flush CSV file
                        out_f.flush()

                    # Rate limiting
                    time.sleep(0.2)

                    # Save checkpoint every 1000
                    if i % 1000 == 0:
                        self.save_checkpoint(i)

        # Save final JSON
        self.save_final_results(output_json, start_time)

        print("\n" + "=" * 80)
        print("VALIDATION COMPLETE!")
        print("=" * 80)
        print(f"Results saved to:")
        print(f"  - {output_csv} (detailed CSV with all addresses)")
        print(f"  - {output_json} (complete JSON with full details)")
        print("=" * 80)

    def save_checkpoint(self, row_num):
        """Save checkpoint"""
        checkpoint = {
            'last_row': row_num,
            'valid_count': self.valid_count,
            'invalid_count': self.invalid_count,
            'timestamp': datetime.now().isoformat()
        }
        with open(f'checkpoint_{row_num}.json', 'w') as f:
            json.dump(checkpoint, f, indent=2)

    def save_final_results(self, output_file, start_time):
        """Save final comprehensive results"""

        elapsed = time.time() - start_time
        total = self.valid_count + self.invalid_count

        # Separate valid and invalid addresses
        valid_addresses = [r for r in self.results if r['validation_status'] == 'VALID']
        invalid_addresses = [r for r in self.results if r['validation_status'] != 'VALID']

        final_data = {
            'summary': {
                'total_addresses': total,
                'valid_count': self.valid_count,
                'invalid_count': self.invalid_count,
                'validation_rate': f"{(self.valid_count/total*100):.2f}%" if total > 0 else "0%",
                'processing_time_minutes': round(elapsed/60, 2),
                'timestamp': datetime.now().isoformat()
            },
            'valid_addresses': valid_addresses,
            'invalid_addresses': invalid_addresses
        }

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(final_data, f, indent=2)

        # Print summary
        print(f"\nTotal addresses: {total:,}")
        print(f"✓ Valid: {self.valid_count:,} ({self.valid_count/total*100:.2f}%)")
        print(f"✗ Invalid: {self.invalid_count:,} ({self.invalid_count/total*100:.2f}%)")
        print(f"\nProcessing time: {elapsed/60:.1f} minutes")
        print(f"Average rate: {total/elapsed:.1f} addresses/second")

        # Show invalid addresses
        if invalid_addresses:
            print(f"\n{'='*80}")
            print(f"INVALID ADDRESSES ({len(invalid_addresses)} total):")
            print('-' * 80)
            for addr in invalid_addresses[:50]:  # Show first 50
                print(f"Row {addr['row_number']:5d}: {addr['original_address']}")
                print(f"           Reason: {addr['error_reason']}")

            if len(invalid_addresses) > 50:
                print(f"\n... and {len(invalid_addresses)-50} more (see JSON file for complete list)")


if __name__ == '__main__':
    validator = ComprehensiveValidator()
    validator.validate_all()
