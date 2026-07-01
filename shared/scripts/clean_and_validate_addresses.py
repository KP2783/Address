#!/usr/bin/env python3
"""
Clean and Validate Ohio Address Data
Parses GeoJSON files and outputs clean, validated addresses
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Tuple

class AddressValidator:
    """Clean and validate address data from GeoJSON files"""

    def __init__(self):
        self.total_processed = 0
        self.total_valid = 0
        self.total_invalid = 0
        self.validation_issues = []

    def parse_geojson_file(self, filepath: str) -> List[Dict]:
        """Parse GeoJSON file with one feature per line"""
        addresses = []
        print(f"\nProcessing: {Path(filepath).name}")

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    if line_num % 10000 == 0:
                        print(f"\r  Reading line {line_num:,}...", end='', flush=True)

                    try:
                        feature = json.loads(line.strip())
                        if feature.get('type') == 'Feature':
                            props = feature.get('properties', {})
                            if not props:
                                continue
                            geom = feature.get('geometry', {})
                            if not geom:
                                continue
                            coords = geom.get('coordinates', [None, None])
                            if not coords or len(coords) < 2:
                                coords = [None, None]

                            addresses.append({
                                'number': props.get('number', ''),
                                'street': props.get('street', ''),
                                'unit': props.get('unit', ''),
                                'city': props.get('city', ''),
                                'district': props.get('district', ''),
                                'region': props.get('region', ''),
                                'postcode': props.get('postcode', ''),
                                'longitude': coords[0] if len(coords) > 0 else None,
                                'latitude': coords[1] if len(coords) > 1 else None,
                                'hash': props.get('hash', '')
                            })
                    except json.JSONDecodeError as e:
                        continue

            print(f"\r  Loaded {len(addresses):,} addresses")
            return addresses

        except Exception as e:
            print(f"\nError reading file: {e}")
            return []

    def validate_address(self, addr: Dict) -> Tuple[bool, List[str]]:
        """Validate an address and return (is_valid, issues)"""
        issues = []

        # Check required fields
        if not addr.get('number'):
            issues.append("Missing house number")

        if not addr.get('street'):
            issues.append("Missing street name")

        if not addr.get('city'):
            issues.append("Missing city")

        # Validate zip code format
        postcode = str(addr.get('postcode', '')).strip()
        if not postcode:
            issues.append("Missing zip code")
        elif not re.match(r'^\d{5}(-\d{4})?$', postcode):
            issues.append(f"Invalid zip code format: {postcode}")

        # Validate coordinates
        lat = addr.get('latitude')
        lon = addr.get('longitude')

        if lat is None or lon is None:
            issues.append("Missing coordinates")
        elif not (-90 <= lat <= 90 and -180 <= lon <= 180):
            issues.append(f"Invalid coordinates: ({lat}, {lon})")

        # Check for Ohio coordinates (roughly)
        if lat and lon:
            # Ohio bounds approximately: 38.4-42.3 N, -84.8--80.5 W
            if not (38.0 <= lat <= 42.5 and -85.0 <= lon <= -80.0):
                issues.append(f"Coordinates outside Ohio: ({lat}, {lon})")

        is_valid = len(issues) == 0
        return is_valid, issues

    def clean_address(self, addr: Dict) -> Dict:
        """Clean and standardize an address"""
        cleaned = addr.copy()

        # Clean street name
        street = str(addr.get('street', '')).strip().upper()
        street = re.sub(r'\s+', ' ', street)  # Remove extra spaces
        cleaned['street'] = street

        # Clean house number
        number = str(addr.get('number', '')).strip()
        cleaned['number'] = number

        # Clean unit
        unit = str(addr.get('unit', '')).strip()
        cleaned['unit'] = unit

        # Clean city name
        city = str(addr.get('city', '')).strip().title()
        city = re.sub(r'\s+', ' ', city)
        cleaned['city'] = city

        # Clean zip code
        postcode = str(addr.get('postcode', '')).strip()
        # Ensure 5-digit format
        if postcode and re.match(r'^\d{5}', postcode):
            cleaned['postcode'] = postcode[:5]
        else:
            cleaned['postcode'] = postcode

        # Ensure region is OH
        cleaned['region'] = 'OH'

        return cleaned

    def format_address_line(self, addr: Dict, include_coords: bool = True) -> str:
        """Format address as a single line"""
        parts = []

        # House number
        if addr.get('number'):
            parts.append(str(addr['number']))

        # Street
        if addr.get('street'):
            parts.append(addr['street'])

        # Unit
        if addr.get('unit'):
            unit = addr['unit']
            if not unit.upper().startswith(('APT', 'UNIT', 'STE', 'SUITE', '#')):
                unit = f"Unit {unit}"
            parts.append(unit)

        # City, State, Zip
        location_parts = []
        if addr.get('city'):
            location_parts.append(addr['city'])
        if addr.get('region'):
            location_parts.append(addr['region'])
        if addr.get('postcode'):
            location_parts.append(addr['postcode'])

        if location_parts:
            parts.append(', '.join(location_parts))

        address_str = ', '.join(parts)

        # Add coordinates if requested
        if include_coords and addr.get('latitude') and addr.get('longitude'):
            address_str += f" | Lat: {addr['latitude']:.6f}, Lon: {addr['longitude']:.6f}"

        return address_str

    def filter_county(self, addresses: List[Dict], county_code: str) -> List[Dict]:
        """Filter addresses by county district code"""
        return [addr for addr in addresses if addr.get('district') == county_code]

    def process_county_file(self, filepath: str, county_name: str) -> List[Dict]:
        """Process a county GeoJSON file"""
        print(f"\n{'='*70}")
        print(f"Processing {county_name} County")
        print(f"{'='*70}")

        # Parse file
        addresses = self.parse_geojson_file(filepath)

        if not addresses:
            print(f"No addresses found in {filepath}")
            return []

        # Clean and validate
        print(f"\nCleaning and validating {len(addresses):,} addresses...")

        valid_addresses = []
        invalid_count = 0

        for i, addr in enumerate(addresses, 1):
            if i % 5000 == 0:
                print(f"\r  Validated {i:,}/{len(addresses):,}...", end='', flush=True)

            # Clean first
            cleaned = self.clean_address(addr)

            # Then validate
            is_valid, issues = self.validate_address(cleaned)

            if is_valid:
                valid_addresses.append(cleaned)
            else:
                invalid_count += 1
                if invalid_count <= 10:  # Store first 10 invalid examples
                    self.validation_issues.append({
                        'address': self.format_address_line(addr, False),
                        'issues': issues
                    })

        print(f"\r  Validated {len(addresses):,} addresses")
        print(f"\n  ✓ Valid addresses: {len(valid_addresses):,}")
        print(f"  ✗ Invalid addresses: {invalid_count:,}")

        self.total_processed += len(addresses)
        self.total_valid += len(valid_addresses)
        self.total_invalid += invalid_count

        return valid_addresses


def main():
    print("="*70)
    print("ADDRESS CLEANER AND VALIDATOR")
    print("Franklin & Delaware Counties, Ohio")
    print("="*70)

    validator = AddressValidator()

    # File paths
    data_dir = Path("/Users/kevinpatel/Address/oh")
    franklin_file = data_dir / "franklin-addresses-county.geojson"
    delaware_file = data_dir / "delaware-addresses-county.geojson"

    # Check files exist
    if not franklin_file.exists():
        print(f"\nERROR: Franklin County file not found: {franklin_file}")
        return

    if not delaware_file.exists():
        print(f"\nERROR: Delaware County file not found: {delaware_file}")
        return

    # Process Franklin County
    franklin_addresses = validator.process_county_file(
        str(franklin_file),
        "Franklin"
    )

    # Process Delaware County
    delaware_addresses = validator.process_county_file(
        str(delaware_file),
        "Delaware"
    )

    # Combine addresses
    all_addresses = franklin_addresses + delaware_addresses

    print(f"\n{'='*70}")
    print("Writing Output Files")
    print(f"{'='*70}")

    # Output 1: addresses.txt - Simple format
    output_file = Path("/Users/kevinpatel/Address/addresses.txt")
    print(f"\nWriting to {output_file}...")

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("CLEAN VALIDATED ADDRESSES - FRANKLIN & DELAWARE COUNTIES, OHIO\n")
        f.write("="*70 + "\n\n")

        # Franklin County
        f.write(f"FRANKLIN COUNTY ({len(franklin_addresses):,} addresses)\n")
        f.write("-"*70 + "\n")
        for addr in franklin_addresses:
            f.write(validator.format_address_line(addr, include_coords=False) + "\n")

        f.write("\n")

        # Delaware County
        f.write(f"DELAWARE COUNTY ({len(delaware_addresses):,} addresses)\n")
        f.write("-"*70 + "\n")
        for addr in delaware_addresses:
            f.write(validator.format_address_line(addr, include_coords=False) + "\n")

    print(f"✓ Saved {len(all_addresses):,} addresses to {output_file}")

    # Output 2: addresses_with_coords.txt - With coordinates
    coords_file = Path("/Users/kevinpatel/Address/addresses_with_coords.txt")
    print(f"\nWriting to {coords_file}...")

    with open(coords_file, 'w', encoding='utf-8') as f:
        f.write("CLEAN VALIDATED ADDRESSES WITH COORDINATES\n")
        f.write("Franklin & Delaware Counties, Ohio\n")
        f.write("="*70 + "\n\n")

        for addr in all_addresses:
            f.write(validator.format_address_line(addr, include_coords=True) + "\n")

    print(f"✓ Saved {len(all_addresses):,} addresses with coordinates to {coords_file}")

    # Output 3: CSV format
    csv_file = Path("/Users/kevinpatel/Address/addresses_clean.csv")
    print(f"\nWriting to {csv_file}...")

    import csv
    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['number', 'street', 'unit', 'city', 'region', 'postcode',
                     'district', 'latitude', 'longitude']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for addr in all_addresses:
            writer.writerow({
                'number': addr.get('number', ''),
                'street': addr.get('street', ''),
                'unit': addr.get('unit', ''),
                'city': addr.get('city', ''),
                'region': addr.get('region', ''),
                'postcode': addr.get('postcode', ''),
                'district': addr.get('district', ''),
                'latitude': addr.get('latitude', ''),
                'longitude': addr.get('longitude', '')
            })

    print(f"✓ Saved {len(all_addresses):,} addresses to CSV: {csv_file}")

    # Summary
    print(f"\n{'='*70}")
    print("SUMMARY")
    print(f"{'='*70}")
    print(f"\nTotal addresses processed: {validator.total_processed:,}")
    print(f"  ✓ Valid: {validator.total_valid:,} ({validator.total_valid/validator.total_processed*100:.1f}%)")
    print(f"  ✗ Invalid: {validator.total_invalid:,} ({validator.total_invalid/validator.total_processed*100:.1f}%)")

    print(f"\nFranklin County: {len(franklin_addresses):,} valid addresses")
    print(f"Delaware County: {len(delaware_addresses):,} valid addresses")
    print(f"Combined Total: {len(all_addresses):,} addresses")

    # Show validation issues examples
    if validator.validation_issues:
        print(f"\n{'='*70}")
        print("VALIDATION ISSUES (First 10 examples)")
        print(f"{'='*70}")
        for i, issue in enumerate(validator.validation_issues[:10], 1):
            print(f"\n{i}. {issue['address']}")
            for problem in issue['issues']:
                print(f"   - {problem}")

    print(f"\n{'='*70}")
    print("✓ ADDRESS CLEANING AND VALIDATION COMPLETE!")
    print(f"{'='*70}\n")


if __name__ == "__main__":
    main()
