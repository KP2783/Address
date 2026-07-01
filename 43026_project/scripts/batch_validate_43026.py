#!/usr/bin/env python3
"""
Batch validation script for 43026 addresses.
This script is designed to work with an AI agent that has search_web capabilities.

Usage:
    1. Reads from addresses_43026_formatted.csv
    2. The AI agent will use this script's logic to validate addresses
    3. Results are saved to validation_results_43026.csv
"""

import csv
import json
import os
import time
import random
import re
from googlesearch import search
from validate_address_google import validate_address, build_search_query

# Updated paths for 43026
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
INPUT_FILE = os.path.join(PROJECT_ROOT, 'data', 'addresses_43026.csv')
OUTPUT_FILE = os.path.join(PROJECT_ROOT, 'output', 'validation_results_43026.csv')

# Ensure output directory exists
os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

def load_addresses(limit=None):
    """Load addresses from input file."""
    addresses = []
    try:
        with open(INPUT_FILE, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for i, row in enumerate(reader):
                if limit and i >= limit:
                    break
                
                # Parse structured CSV: number,street,unit,city,region,postcode
                number = row.get('number', '').strip()
                street = row.get('street', '').strip()
                unit = row.get('unit', '').strip()
                city = row.get('city', '').strip()
                region = row.get('region', '').strip()
                postcode = row.get('postcode', '').strip()
                
                if number and street:
                    # Clean street name (strip Gxx, BLDG xx)
                    street = re.sub(r'\sG\d+$', '', street)
                    street = re.sub(r'\sBLDG\s\d+$', '', street)
                    
                    addr_parts = [number, street]
                    if unit:
                        addr_parts.append(unit)
                    
                    base_addr = " ".join(addr_parts)
                    full_addr = f"{base_addr}, {city}, {region}, {postcode}"
                    
                    addresses.append({'address': full_addr})
                elif row.get('address'): # Fallback for formatted style
                    addresses.append({'address': row.get('address').strip().strip('"')})

    except FileNotFoundError:
        print(f"Error: Input file {INPUT_FILE} not found.")
        return []
        
    return addresses

def get_processed_addresses():
    """Get list of already processed addresses."""
    processed = set()
    
    # Check validation results (Has Header)
    if os.path.isfile(OUTPUT_FILE):
        try:
            with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if 'address' in row:
                        processed.add(row['address'])
        except Exception as e:
            print(f"Error reading processed file: {e}")

    # Check excluded addresses (NO Header, Column 0)
    excluded_file = os.path.join(PROJECT_ROOT, 'output', 'excluded_addresses.csv')
    if os.path.isfile(excluded_file):
        try:
            with open(excluded_file, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                for row in reader:
                    if row:
                        processed.add(row[0])
        except Exception as e:
            print(f"Error reading excluded file: {e}")

    # Check manual review file explicitly
    manual_file = os.path.join(PROJECT_ROOT, 'output', 'manual_review_needed.txt')
    if os.path.isfile(manual_file):
        try:
            with open(manual_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        processed.add(line.strip())
        except Exception as e:
            print(f"Error reading manual review file: {e}")

    # Check unknown files (legacy support)
    output_dir = os.path.dirname(OUTPUT_FILE)
    try:
        for fname in os.listdir(output_dir):
            if 'unknown' in fname.lower() and fname.endswith('.csv'):
                fpath = os.path.join(output_dir, fname)
                try:
                    with open(fpath, 'r', encoding='utf-8') as f:
                        reader = csv.reader(f)
                        for row in reader:
                            if row:
                                processed.add(row[0])
                except Exception as e:
                     pass
    except Exception as e:
        print(f"Error scanning unknowns: {e}")
        
    return processed

def save_result(result: dict):
    """Save a single validation result to CSV."""
    file_exists = os.path.isfile(OUTPUT_FILE)
    
    with open(OUTPUT_FILE, 'a', newline='', encoding='utf-8') as f:
        fieldnames = ['address', 'classification', 'property_type', 'source']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        
        if not file_exists:
            writer.writeheader()
            
        writer.writerow({
            'address': result['address'],
            'classification': result['classification'],
            'property_type': result.get('property_type', 'unknown'),
            'source': result.get('source', 'pending')
        })

def perform_google_search(query):
    """Perform Google search and return combined snippet."""
    try:
        # Fetch top 3 results
        print(f"Searching for: {query}")
        results = search(query, num_results=3, advanced=True)
        snippets = []
        count = 0
        for result in results:
            count += 1
            content = f"{result.title}\n{result.description}\n{result.url}"
            snippets.append(content)
        
        print(f"Found {count} results for {query}")
        return "\n\n".join(snippets)
    except Exception as e:
        print(f"Search error for '{query}': {e}")
        return ""

def get_next_batch(batch_size=10, offset=0):
    """Get next batch of addresses to validate."""
    processed = get_processed_addresses()
    print(f"DEBUG: Found {len(processed)} processed addresses.")
    
    addresses = load_addresses()
    remaining = [a['address'] for a in addresses if a['address'] not in processed]
    
    # Apply offset if needed, but usually we just want the next logical batch of unprocessed items
    # If offset is provided relative to *remaining*, use it.
    batch = remaining[offset:offset + batch_size]
    return batch

def process_search_result(address: str, search_result: str) -> dict:
    """Process a single search result and return validation."""
    return validate_address(address, search_result)

def main():
    print("Starting batch validation for 43026 (Library Mode)...")
    
    all_addresses = load_addresses()
    print(f"Total input addresses: {len(all_addresses)}")
    
    processed = get_processed_addresses()
    print(f"Already processed: {len(processed)}")
    
    remaining = [a for a in all_addresses if a['address'] not in processed]
    print(f"Remaining to process: {len(remaining)}")
    
    try:
        from googlesearch import search
    except ImportError:
        print("googlesearch-python not installed or found. Cannot run in standalone mode.")
        return

    for i, addr_obj in enumerate(remaining):
        address = addr_obj['address']
        print(f"[{i+1}/{len(remaining)}] Validating: {address}")
        
        query = build_search_query(address)
        search_result = perform_google_search(query)
        
        validation = validate_address(address, search_result)
        save_result(validation)
        
        # Respect rate limits
        sleep_time = random.uniform(2.0, 5.0)
        time.sleep(sleep_time)

if __name__ == "__main__":
    main()
