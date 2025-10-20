# Address Extractor

A Python script to extract addresses from open-source address databases, with filtering by state and zip code.

## Features

- Extract addresses from OpenAddresses open-source database
- Filter by state (US states)
- Filter by zip code(s)
- Output to CSV format
- Support for processing existing CSV files

## Installation

1. Install Python 3.7 or higher

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Basic Examples

**Extract all addresses for a state:**
```bash
python extract_addresses.py --state CA --zip all
```

**Extract addresses for specific zip codes:**
```bash
python extract_addresses.py --state CA --zip 94102 94103 94104
```

**Filter an existing CSV file by zip code:**
```bash
python extract_addresses.py --input addresses.csv --zip 10001 10002 --output filtered.csv
```

**Download state data without filtering:**
```bash
python extract_addresses.py --state NY --zip all --download-only
```

### Command-Line Arguments

- `--state, -s`: State code (e.g., CA, NY, TX)
- `--zip, -z`: Zip code(s) to filter, or "all" for all zip codes (required)
- `--input, -i`: Input CSV file (if you already have address data)
- `--output, -o`: Output CSV file (default: addresses_<state>_filtered.csv)
- `--download-only`: Only download the dataset without filtering

## Data Sources

This script uses data from:
- **OpenAddresses** (https://openaddresses.io/) - A free and open global address database

## Output Format

The script outputs CSV files with the following typical fields (varies by data source):
- Street number and name
- City
- State
- Zip/Postal code
- Latitude/Longitude (if available)

## Alternative Usage

If the OpenAddresses API is unavailable, you can:

1. **Download data manually** from https://openaddresses.io/
2. **Use the script to filter** your downloaded CSV:
   ```bash
   python extract_addresses.py --input your_addresses.csv --zip 12345 --output filtered.csv
   ```

## Examples

**Extract California addresses for San Francisco zip codes:**
```bash
python extract_addresses.py --state CA --zip 94102 94103 94104 94105 --output sf_addresses.csv
```

**Extract New York addresses for Manhattan:**
```bash
python extract_addresses.py --state NY --zip 10001 10002 10003 10004 10005
```

**Filter existing data:**
```bash
python extract_addresses.py --input raw_addresses.csv --zip 90210 --output beverly_hills.csv
```

## Troubleshooting

**"Could not fetch from OpenAddresses API"**
- The API might be temporarily unavailable
- Download data manually from https://openaddresses.io/ and use the `--input` flag

**"Could not find zip code column"**
- The CSV might have a different column name
- The script will show available columns and save all data

**"No addresses extracted"**
- The zip code might not exist in the dataset
- Try using `--zip all` to see all available data first

## License

This script is for educational and research purposes. Please respect the licenses of the data sources you use.
