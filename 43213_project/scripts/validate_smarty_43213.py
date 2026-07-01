#!/usr/bin/env python3
"""
Address validation for 43213 using Smarty Streets API.
- Auto-classifies residential street types (CT, LN, WAY, CIR, PL, LOOP, DR, etc.)
- Uses Smarty API for uncertain streets (RD, ST, AVE, BLVD, PKWY, etc.)
- Fixes bad city names (Truro Twp, Jefferson Twp -> Columbus)
- Returns USPS-standardized addresses with RDI classification
"""

import csv
import json
import os
import re
import time
import urllib.request
import urllib.parse
import urllib.error
from typing import Dict, List

# API Credentials
AUTH_ID = "3a23fb9c-0d15-ab4c-646f-4454c6625a8f"
AUTH_TOKEN = "kdQ43J7IGlv1Hz1qcD6R"

# File paths
INPUT_FILE = '/Users/kevinpatel/Address/43213_project/data/addresses_43213_formatted.csv'
OUTPUT_FILE = '/Users/kevinpatel/Address/43213_project/output/smarty_validation_results.csv'

# API endpoint
API_URL = "https://us-street.api.smarty.com/street-address"

# Street types that are almost always residential
RESIDENTIAL_STREET_TYPES = ['CT', 'LN', 'WAY', 'CIR', 'PL', 'LOOP', 'DR', 'TRL', 'RUN', 'XING', 'PATH', 'WALK']

# Street types that need API verification
UNCERTAIN_STREET_TYPES = ['RD', 'ST', 'AVE', 'BLVD', 'PKWY', 'HWY', 'PIKE']


def is_residential_street_type(address: str) -> bool:
    """Check if address has a residential-only street type."""
    addr_upper = address.upper()

    # Suite/STE indicators need API verification
    if ' STE ' in addr_upper or ' SUITE ' in addr_upper:
        return False

    for st_type in RESIDENTIAL_STREET_TYPES:
        if f' {st_type},' in addr_upper or f' {st_type} ' in addr_upper:
            return True

    return False


def parse_address(full_address: str) -> Dict[str, str]:
    """Parse a full address string into components for Smarty API."""
    parts = [p.strip() for p in full_address.split(',')]

    if len(parts) >= 4:
        street = parts[0]
        city = parts[1]
        state = parts[2].strip()
        zipcode = parts[3].strip()
    elif len(parts) >= 3:
        street = parts[0]
        city = parts[1]
        state_zip = parts[2].strip()
        match = re.match(r'([A-Z]{2})\s+(\d{5}(?:-\d{4})?)', state_zip)
        if match:
            state = match.group(1)
            zipcode = match.group(2)
        else:
            state = state_zip[:2] if len(state_zip) >= 2 else "OH"
            zipcode = "43213"
    else:
        street = parts[0] if parts else ""
        city = "Columbus"
        state = "OH"
        zipcode = "43213"

    # Fix township names to proper USPS cities
    city_upper = city.upper().strip()
    if city_upper in ('TRURO TWP', 'JEFFERSON TWP', ''):
        city = 'Columbus'

    return {
        'street': street,
        'city': city,
        'state': state,
        'zipcode': zipcode
    }


def validate_batch(addresses: List[Dict]) -> List[Dict]:
    """Validate a batch of addresses using Smarty API."""
    request_body = []
    for addr in addresses:
        request_body.append({
            "street": addr['street'],
            "city": addr['city'],
            "state": addr['state'],
            "zipcode": addr['zipcode'],
            "match": "invalid"
        })

    params = urllib.parse.urlencode({
        'auth-id': AUTH_ID,
        'auth-token': AUTH_TOKEN
    })
    url = f"{API_URL}?{params}"

    headers = {'Content-Type': 'application/json'}
    data = json.dumps(request_body).encode('utf-8')

    req = urllib.request.Request(url, data=data, headers=headers, method='POST')

    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode('utf-8'))
            return result
    except urllib.error.HTTPError as e:
        print(f"HTTP Error {e.code}: {e.reason}")
        if e.code == 402:
            print("Payment required - API limit reached")
        return []
    except Exception as e:
        print(f"Error: {e}")
        return []


def get_rdi_classification(rdi: str) -> str:
    """Convert RDI indicator to classification."""
    if rdi == "Residential":
        return "RESIDENTIAL"
    elif rdi == "Commercial":
        return "COMMERCIAL"
    else:
        return "UNKNOWN"


def main():
    # Load already processed addresses
    already_processed = set()
    if os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                already_processed.add(row['address'])
        print(f"Already processed: {len(already_processed)} addresses")

    # Load and categorize addresses
    print(f"Loading addresses from {INPUT_FILE}")
    auto_residential = []
    needs_api = []

    with open(INPUT_FILE, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            addr = row['address']
            if addr in already_processed:
                continue

            if is_residential_street_type(addr):
                auto_residential.append(addr)
            else:
                needs_api.append(addr)

    print(f"\n=== Smart Classification Plan ===")
    print(f"Auto-classify as RESIDENTIAL: {len(auto_residential)}")
    print(f"Need Smarty API verification: {len(needs_api)}")
    print(f"Total new addresses: {len(auto_residential) + len(needs_api)}")

    # Write auto-classified residential addresses
    fieldnames = ['address', 'classification', 'rdi', 'dpv_match', 'validated_address', 'source']

    if auto_residential:
        print(f"\nWriting {len(auto_residential)} auto-classified RESIDENTIAL addresses...")
        file_exists = os.path.exists(OUTPUT_FILE) and os.path.getsize(OUTPUT_FILE) > 0
        with open(OUTPUT_FILE, 'a', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            if not file_exists:
                writer.writeheader()
            for addr in auto_residential:
                writer.writerow({
                    'address': addr,
                    'classification': 'RESIDENTIAL',
                    'rdi': 'Residential',
                    'dpv_match': 'auto',
                    'validated_address': addr,
                    'source': 'pattern_match'
                })

    # Process uncertain addresses with Smarty API
    if not needs_api:
        print("\nNo addresses need API verification!")
    else:
        print(f"\nProcessing {len(needs_api)} addresses with Smarty API...")
        batch_size = 100
        total_processed = 0

        for i in range(0, len(needs_api), batch_size):
            batch = needs_api[i:i+batch_size]
            batch_num = i // batch_size + 1
            total_batches = (len(needs_api) - 1) // batch_size + 1
            print(f"API batch {batch_num}/{total_batches} ({len(batch)} addresses)")

            parsed_batch = [parse_address(addr) for addr in batch]

            api_results = validate_batch(parsed_batch)

            if not api_results and len(parsed_batch) > 0:
                print("\n*** API limit reached or error! ***")
                print(f"Processed {total_processed} API addresses before limit")
                break

            result_map = {res.get('input_index', 0): res for res in api_results}

            batch_results = []
            for j, orig_addr in enumerate(batch):
                api_res = result_map.get(j, {})
                metadata = api_res.get('metadata', {})
                rdi = metadata.get('rdi', '')
                analysis = api_res.get('analysis', {})
                dpv_match = analysis.get('dpv_match_code', '')

                # Build validated address from API response
                components = api_res.get('components', {})
                if components:
                    validated = f"{api_res.get('delivery_line_1', '')}, {components.get('city_name', '')}, {components.get('state_abbreviation', '')} {components.get('zipcode', '')}-{components.get('plus4_code', '')}"
                else:
                    validated = orig_addr

                batch_results.append({
                    'address': orig_addr,
                    'classification': get_rdi_classification(rdi),
                    'rdi': rdi,
                    'dpv_match': dpv_match,
                    'validated_address': validated,
                    'source': 'smarty_api'
                })

            file_exists = os.path.exists(OUTPUT_FILE) and os.path.getsize(OUTPUT_FILE) > 0
            with open(OUTPUT_FILE, 'a', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                if not file_exists:
                    writer.writeheader()
                writer.writerows(batch_results)

            total_processed += len(batch_results)

            if i + batch_size < len(needs_api):
                time.sleep(0.5)

        print(f"\nAPI processing complete: {total_processed} addresses")

    # Final summary
    counts = {}
    total_in_file = 0
    with open(OUTPUT_FILE, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            c = row['classification']
            counts[c] = counts.get(c, 0) + 1
            total_in_file += 1

    print(f"\n=== Final Results Summary ===")
    print(f"Total in file: {total_in_file}")
    for k, v in sorted(counts.items()):
        pct = v / total_in_file * 100
        print(f"  {k}: {v} ({pct:.1f}%)")

    source_counts = {}
    with open(OUTPUT_FILE, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            src = row.get('source', 'unknown')
            source_counts[src] = source_counts.get(src, 0) + 1

    print(f"\nBy source:")
    for src, cnt in source_counts.items():
        print(f"  {src}: {cnt}")

    print(f"\nResults saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
