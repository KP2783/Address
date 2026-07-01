#!/usr/bin/env python3
"""
Address Validation for 43026 - Preserves Unit Information
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

    def validate_row(self, address, row_num):
        """Validate a single address"""
        result = {
            'row_number': row_num,
            'original_address': address,
            'validation_status': 'PENDING',
            'matched_address': '',
            'latitude': '',
            'longitude': '',
            'error_reason': ''
        }

        # Census API validation
        api_valid, api_data = self.validate_with_census(address)

        if api_valid:
            result['matched_address'] = api_data['matched_address']
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
        input_file = 'addresses_43026_residential.csv'
        output_csv = 'validation_results_43026_detailed.csv'
        output_json = 'validation_results_43026_full.json'
        log_file = 'validation_43026_complete.log'

        print("=" * 80)
        print("ADDRESS VALIDATION FOR 43026 - WITH UNIT PRESERVATION")
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
            reader = csv.reader(f)
            next(reader)  # Skip header

            for i, row in enumerate(reader, 1):
                # Skip already processed rows
                if i <= resume_from_row:
                    continue

                # Join all columns to get full address
                address = ', '.join(row).strip()
                result = self.validate_row(address, i)
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
