#!/usr/bin/env python3
"""
Address validation for 43213 using Google Address Validation API.
- Validates all addresses through Google for USPS-standardized output
- Fixes bad city names (Truro Twp, Jefferson Twp)
- Returns validated addresses with residential/commercial verdicts
- Supports resume (skips already-processed addresses)
"""

import csv
import json
import os
import re
import time
import urllib.request
import urllib.error
from typing import Dict, List, Optional

# Google API Key
GOOGLE_API_KEY = "AIzaSyDyCcX7IAYBd6N99qD5wPBRjDUv3se7LDE"

# File paths
INPUT_FILE = '/Users/kevinpatel/Address/43213_project/data/addresses_43213_formatted.csv'
OUTPUT_FILE = '/Users/kevinpatel/Address/43213_project/output/google_validation_results.csv'

# API endpoint
API_URL = "https://addressvalidation.googleapis.com/v1:validateAddress"

FIELDNAMES = [
    'address', 'validated_address', 'classification',
    'city', 'state', 'zip', 'zip_plus4',
    'verdict', 'granularity', 'has_unconfirmed',
    'latitude', 'longitude', 'source'
]


def parse_input_address(full_address: str) -> Dict[str, str]:
    """Parse formatted address into components, fixing township names."""
    parts = [p.strip() for p in full_address.split(',')]

    street = parts[0] if len(parts) >= 1 else ''
    city = parts[1] if len(parts) >= 2 else 'Columbus'
    state = parts[2].strip() if len(parts) >= 3 else 'OH'
    zipcode = parts[3].strip() if len(parts) >= 4 else '43213'

    # Fix township names
    city_upper = city.upper().strip()
    if city_upper in ('TRURO TWP', 'JEFFERSON TWP', ''):
        city = 'Columbus'

    return {
        'street': street,
        'city': city,
        'state': state,
        'zipcode': zipcode
    }


def validate_address_google(address: str) -> Optional[Dict]:
    """Call Google Address Validation API for a single address."""
    parsed = parse_input_address(address)

    request_body = {
        "address": {
            "regionCode": "US",
            "addressLines": [
                parsed['street'],
                f"{parsed['city']}, {parsed['state']} {parsed['zipcode']}"
            ]
        },
        "enableUspsCass": True
    }

    url = f"{API_URL}?key={GOOGLE_API_KEY}"
    headers = {'Content-Type': 'application/json'}
    data = json.dumps(request_body).encode('utf-8')

    req = urllib.request.Request(url, data=data, headers=headers, method='POST')

    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            return json.loads(response.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8') if e.fp else ''
        print(f"HTTP Error {e.code}: {e.reason}")
        if error_body:
            print(f"  Detail: {error_body[:200]}")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None


def parse_google_result(orig_address: str, result: Dict) -> Dict:
    """Parse Google API response into our CSV row format."""
    row = {
        'address': orig_address,
        'validated_address': '',
        'classification': 'UNKNOWN',
        'city': '',
        'state': '',
        'zip': '',
        'zip_plus4': '',
        'verdict': '',
        'granularity': '',
        'has_unconfirmed': '',
        'latitude': '',
        'longitude': '',
        'source': 'google_api'
    }

    if not result or 'result' not in result:
        row['verdict'] = 'NO_RESULT'
        return row

    r = result['result']

    # Verdict
    verdict = r.get('verdict', {})
    row['verdict'] = verdict.get('validationGranularity', 'UNKNOWN')
    row['granularity'] = verdict.get('validationGranularity', '')
    row['has_unconfirmed'] = str(verdict.get('hasUnconfirmedComponents', False))

    # Formatted address
    addr_obj = r.get('address', {})
    row['validated_address'] = addr_obj.get('formattedAddress', orig_address)

    # Extract components
    components = addr_obj.get('addressComponents', [])
    for comp in components:
        ctype = comp.get('componentType', '')
        text = comp.get('componentName', {}).get('text', '')
        if ctype == 'locality':
            row['city'] = text
        elif ctype == 'administrative_area_level_1':
            row['state'] = text
        elif ctype == 'postal_code':
            row['zip'] = text
        elif ctype == 'postal_code_suffix':
            row['zip_plus4'] = text

    # Geocode
    geocode = r.get('geocode', {})
    location = geocode.get('location', {})
    row['latitude'] = str(location.get('latitude', ''))
    row['longitude'] = str(location.get('longitude', ''))

    # Classification from metadata (most reliable)
    metadata = r.get('metadata', {})
    is_residential = metadata.get('residential', False)
    is_business = metadata.get('business', False)

    if is_residential and not is_business:
        row['classification'] = 'RESIDENTIAL'
    elif is_business and not is_residential:
        row['classification'] = 'COMMERCIAL'
    elif is_residential and is_business:
        row['classification'] = 'MIXED'
    else:
        # Fallback to USPS addressRecordType
        usps = r.get('uspsData', {})
        address_type = usps.get('addressRecordType', '')
        if address_type in ('S', 'H', 'R'):
            row['classification'] = 'RESIDENTIAL'
        elif address_type in ('F', 'G', 'P'):
            row['classification'] = 'COMMERCIAL'
        else:
            row['classification'] = 'UNKNOWN'

    return row


def main():
    # Load already processed addresses
    already_processed = set()
    if os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                already_processed.add(row['address'])
        print(f"Already processed: {len(already_processed)} addresses")

    # Load addresses
    print(f"Loading addresses from {INPUT_FILE}")
    all_addresses = []
    with open(INPUT_FILE, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            addr = row['address']
            if addr not in already_processed:
                all_addresses.append(addr)

    print(f"Addresses to validate: {len(all_addresses)}")

    if not all_addresses:
        print("Nothing to do!")
        return

    # Initialize output file if needed
    file_exists = os.path.exists(OUTPUT_FILE) and os.path.getsize(OUTPUT_FILE) > 0
    if not file_exists:
        with open(OUTPUT_FILE, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
            writer.writeheader()

    # Process addresses one at a time (Google API doesn't support batch)
    total_processed = 0
    errors = 0
    batch_buffer = []
    batch_write_size = 50  # write to CSV every 50 addresses

    for i, addr in enumerate(all_addresses):
        if (i + 1) % 100 == 0 or i == 0:
            print(f"Processing {i+1}/{len(all_addresses)}...")

        result = validate_address_google(addr)

        if result is None:
            errors += 1
            if errors >= 5:
                print(f"\n*** Too many errors ({errors}), stopping. ***")
                print(f"Processed {total_processed} addresses before stopping.")
                break
            # Still record the failed address
            row = {f: '' for f in FIELDNAMES}
            row['address'] = addr
            row['verdict'] = 'API_ERROR'
            row['source'] = 'google_api'
            row['classification'] = 'PENDING'
            batch_buffer.append(row)
        else:
            errors = 0  # reset consecutive error count
            parsed = parse_google_result(addr, result)
            batch_buffer.append(parsed)
            total_processed += 1

        # Flush buffer periodically
        if len(batch_buffer) >= batch_write_size:
            with open(OUTPUT_FILE, 'a', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
                writer.writerows(batch_buffer)
            batch_buffer = []

        # Rate limit: ~10 requests/sec to stay safe
        time.sleep(0.1)

    # Flush remaining
    if batch_buffer:
        with open(OUTPUT_FILE, 'a', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
            writer.writerows(batch_buffer)

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
    print(f"Total validated: {total_in_file}")
    for k, v in sorted(counts.items()):
        pct = v / total_in_file * 100
        print(f"  {k}: {v} ({pct:.1f}%)")

    print(f"\nResults saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
