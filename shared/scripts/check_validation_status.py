#!/usr/bin/env python3
"""
Check validation status and show invalid addresses
"""

import json
import sys

def check_status():
    # Try to find the most recent intermediate file
    import glob
    import os

    files = glob.glob('validation_results_intermediate_*.json')
    if files:
        # Get the most recent one
        latest = max(files, key=lambda x: int(x.split('_')[-1].replace('.json', '')))

        with open(latest, 'r') as f:
            data = json.load(f)

        print("=" * 80)
        print("VALIDATION STATUS")
        print("=" * 80)
        print(f"Progress: {data['total_checked']:,} addresses validated")
        print(f"✓ Valid: {data['valid_count']:,} ({data['valid_count']/data['total_checked']*100:.2f}%)")
        print(f"✗ Invalid: {data['invalid_count']:,} ({data['invalid_count']/data['total_checked']*100:.2f}%)")
        print("=" * 80)

        # Try to read the full validation file to get error details
        try:
            with open('validation_results_full.json', 'r') as f:
                full_data = json.load(f)

            if full_data.get('errors'):
                print("\nINVALID ADDRESSES FOUND:")
                print("-" * 80)
                for i, error in enumerate(full_data['errors'][:20], 1):
                    print(f"{i}. {error['address']}")
                    print(f"   Reason: {error['reason']}")
                    print()
        except FileNotFoundError:
            print("\nNote: Full results file not yet available (validation still in progress)")
    else:
        print("No validation results found yet")

if __name__ == '__main__':
    check_status()
