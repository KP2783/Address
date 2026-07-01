#!/usr/bin/env python3
"""
Address Validation for 43229 - Preserves Unit Information
Validates building address via Census API and preserves original unit designations
"""

import csv
import time
import json
import urllib.request
import urllib.parse
import urllib.error
from datetime import datetime

class UnitPreservingValidator:
    def __init__(self):
        self.census_api_url = "https://geocoding.geo.census.gov/geocoder/locations/onelineaddress"
        self.results = []
        self.valid_count = 0
        self.invalid_count = 0
        self.checkpoint_interval = 1000

    def format_address_for_census(self, row):
        """Format address for Census API - includes unit"""
        parts = []
        if row.get('number'): parts.append(row['number'])
        if row.get('street'): parts.append(row['street'])
        if row.get('unit'): parts.append(row['unit'])  # Include unit for validation
        if row.get('city'): parts.append(row['city'])
        if row.get('region'): parts.append(row['region'])
        if row.get('postcode'): parts.append(row['postcode'])
        return ', '.join(parts)

    def format_original_address(self, row):
        """Format original address for display"""
        parts = []
        if row.get('number'): parts.append(row['number'])
        if row.get('street'): parts.append(row['street'])
        city = row.get('city', '')
        region = row.get('region', '')
        postcode = row.get('postcode', '')

        if city and region and postcode:
            parts.append(f"{city}, {region}, {postcode}")

        return ' '.join(parts)

    def reconstruct_address_with_unit(self, matched_address, original_unit):
        """
        Reconstructs the validated address with the original unit preserved

        Census returns: "6665 HUNTLEY RD, COLUMBUS, OH, 43229"
        Original unit: "UNIT G"
        Result: "6665 HUNTLEY RD, UNIT G, COLUMBUS, OH, 43229"
        """
        if not original_unit or original_unit.strip() == '':
            return matched_address

        # Split the matched address at the first comma
        # Format is typically: "STREET ADDRESS, CITY, STATE, ZIP"
        parts = matched_address.split(',', 1)

        if len(parts) >= 2:
            street_part = parts[0].strip()
            rest_part = parts[1].strip()

            # Reconstruct with unit inserted after street address
            return f"{street_part}, {original_unit.strip()}, {rest_part}"
        else:
            # Fallback: just append unit at the end
            return f"{matched_address}, {original_unit.strip()}"

    def validate_format(self, row):
        """Check if address has proper format"""
        issues = []

        if not row.get('number') or not str(row['number']).strip():
            issues.append('Missing house number')
        if not row.get('street') or not str(row['street']).strip():
            issues.append('Missing street name')
        if not row.get('city') or not str(row['city']).strip():
            issues.append('Missing city')
        if not row.get('postcode') or not str(row['postcode']).strip():
            issues.append('Missing zip code')
        else:
            zipcode = str(row['postcode']).strip()
            if not zipcode.isdigit() or len(zipcode) != 5:
                issues.append(f'Invalid zip format: {zipcode}')
            if zipcode != '43229':  # Updated for 43229
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

    def validate_row(self, row, row_num):
        """Validate a single address row"""
        original_address = self.format_original_address(row)
        original_unit = row.get('unit', '').strip()

        result = {
            'row_number': row_num,
            'original_address': original_address,
            'original_unit': original_unit,
            'validation_status': 'PENDING',
            'format_valid': False,
            'census_valid': False,
            'matched_address': '',
            'latitude': '',
            'longitude': '',
            'error_reason': ''
        }

        # Step 1: Format validation
        format_valid, format_issues = self.validate_format(row)
        result['format_valid'] = format_valid

        if not format_valid:
            result['validation_status'] = 'INVALID'
            result['error_reason'] = '; '.join(format_issues)
            self.invalid_count += 1
            return result

        # Step 2: Census API validation
        census_address = self.format_address_for_census(row)
        api_valid, api_data = self.validate_with_census(census_address)
        result['census_valid'] = api_valid

        if api_valid:
            # Get the matched address from Census
            census_matched = api_data['matched_address']

            # Reconstruct with original unit preserved
            final_address = self.reconstruct_address_with_unit(census_matched, original_unit)

            result['matched_address'] = final_address
            result['latitude'] = api_data['coordinates'].get('y', '')
            result['longitude'] = api_data['coordinates'].get('x', '')
            result['validation_status'] = 'VALID'
            self.valid_count += 1
        else:
            result['validation_status'] = 'INVALID'
            result['error_reason'] = api_data.get('error', 'Unknown error')
            self.invalid_count += 1

        return result

    def save_checkpoint(self, output_csv, output_json):
        """Save current results to files"""
        # Save CSV
        with open(output_csv, 'w', newline='', encoding='utf-8') as f:
            if self.results:
                fieldnames = self.results[0].keys()
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(self.results)

        # Save JSON
        with open(output_json, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2)

    def load_checkpoint(self, output_csv):
        """Load existing validation results from checkpoint"""
        import os
        if not os.path.exists(output_csv):
            return 0

        print(f"Found existing checkpoint: {output_csv}")
        with open(output_csv, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Convert string booleans back to actual booleans
                row['format_valid'] = row['format_valid'] == 'True'
                row['census_valid'] = row['census_valid'] == 'True'
                row['row_number'] = int(row['row_number'])

                self.results.append(row)

                # Update counters
                if row['validation_status'] == 'VALID':
                    self.valid_count += 1
                else:
                    self.invalid_count += 1

        resume_from = len(self.results)
        print(f"Loaded {resume_from} previously validated addresses")
        print(f"  Valid: {self.valid_count}, Invalid: {self.invalid_count}")
        print(f"Resuming from row {resume_from + 1}...")
        print()
        return resume_from

    def validate_all(self):
        """Validate all addresses"""
        input_file = 'addresses_43229.csv'
        output_csv = 'validation_results_43229_detailed.csv'
        output_json = 'validation_results_43229_full.json'
        log_file = 'validation_43229_complete.log'

        print("=" * 80)
        print("ADDRESS VALIDATION FOR 43229 - WITH UNIT PRESERVATION")
        print("=" * 80)
        print(f"Input: {input_file}")
        print(f"Output CSV: {output_csv}")
        print(f"Output JSON: {output_json}")
        print(f"Log file: {log_file}")
        print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        print()

        # Load checkpoint if it exists
        resume_from_row = self.load_checkpoint(output_csv)

        # Open log file
        log = open(log_file, 'w', encoding='utf-8')

        def log_print(msg):
            """Print and log simultaneously"""
            print(msg)
            log.write(msg + '\n')
            log.flush()

        # Read and validate addresses
        with open(input_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)

            for i, row in enumerate(reader, 1):
                # Skip already processed rows
                if i <= resume_from_row:
                    continue

                result = self.validate_row(row, i)
                self.results.append(result)

                # Show progress every 100 addresses
                if i % 100 == 0:
                    elapsed = i / 100 * 0.5  # Rough estimate at 2 addr/sec
                    log_print(f"[{i:5d}] Processed | Valid: {self.valid_count:5d} | "
                             f"Invalid: {self.invalid_count:5d} | "
                             f"Est. time: {elapsed:.1f}s")

                # Save checkpoint every 1000 addresses
                if i % self.checkpoint_interval == 0:
                    self.save_checkpoint(output_csv, output_json)
                    log_print(f">>> Checkpoint saved at row {i}")

                # Show first 20 results in detail
                if i <= 20:
                    status_icon = "✓" if result['validation_status'] == 'VALID' else "✗"
                    log_print(f"[{i:5d}] {status_icon} {result['original_address']}")
                    if result['original_unit']:
                        log_print(f"        Unit: {result['original_unit']}")
                    if result['validation_status'] == 'VALID':
                        log_print(f"        → {result['matched_address']}")
                    else:
                        log_print(f"        → ERROR: {result['error_reason']}")
                    log_print("")

                # Rate limiting
                time.sleep(0.5)

        # Final save
        self.save_checkpoint(output_csv, output_json)

        # Summary
        total = len(self.results)
        valid_pct = (self.valid_count / total * 100) if total > 0 else 0
        invalid_pct = (self.invalid_count / total * 100) if total > 0 else 0

        log_print("")
        log_print("=" * 80)
        log_print("VALIDATION COMPLETE")
        log_print("=" * 80)
        log_print(f"Total addresses: {total:,}")
        log_print(f"Valid: {self.valid_count:,} ({valid_pct:.2f}%)")
        log_print(f"Invalid: {self.invalid_count:,} ({invalid_pct:.2f}%)")
        log_print(f"Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        log_print("=" * 80)

        # Show sample of addresses with units that were validated
        unit_addresses = [r for r in self.results if r['original_unit'] and r['validation_status'] == 'VALID']
        if unit_addresses:
            log_print("")
            log_print("SAMPLE UNIT ADDRESSES (VALIDATED WITH UNITS PRESERVED):")
            log_print("-" * 80)
            for result in unit_addresses[:10]:
                log_print(f"Original: {result['original_address']}, {result['original_unit']}")
                log_print(f"Validated: {result['matched_address']}")
                log_print("")

        log.close()

        print(f"\nResults saved to:")
        print(f"  - {output_csv}")
        print(f"  - {output_json}")
        print(f"  - {log_file}")

def main():
    validator = UnitPreservingValidator()
    validator.validate_all()

if __name__ == '__main__':
    main()
