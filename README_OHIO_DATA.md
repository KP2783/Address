# Ohio Address Data Extraction - Complete Solution

## What's Included

This repository contains tools and sample data for extracting Ohio address data by state and zip code.

### Scripts

1. **extract_addresses.py** - Main extraction and filtering script
   - Works with any CSV address file
   - Filters by zip code(s)
   - Outputs to CSV format

2. **download_ohio_addresses.py** - ArcGIS REST API downloader
   - Downloads from ArcGIS FeatureServer endpoints
   - Supports batch downloading
   - Converts to CSV format

3. **download_osm_ohio_addresses.py** - OpenStreetMap downloader
   - Downloads from Overpass API
   - Supports city-based or bbox queries
   - Free and open-source data

### Sample Data Files

1. **ohio_comprehensive_sample.csv** - 566 addresses from 8 major Ohio cities
   - Columbus, Cleveland, Cincinnati, Toledo, Akron, Dayton, Youngstown, Canton
   - 40 different zip codes
   - Realistic address data with coordinates

2. **ohio_all_extracted.csv** - All 566 addresses (unfiltered)

3. **ohio_major_cities.csv** - Filtered subset (46 addresses from 3 major cities)

### Documentation

- **OHIO_ADDRESS_DATA_GUIDE.md** - Comprehensive guide to obtaining real Ohio address data
- **README.md** - Main project documentation

## Quick Start

### Extract All Ohio Addresses

```bash
python extract_addresses.py --input ohio_comprehensive_sample.csv --zip all --output results.csv
```

### Extract Specific Zip Codes

```bash
# Single zip code
python extract_addresses.py --input ohio_comprehensive_sample.csv --zip 43215 --output columbus.csv

# Multiple zip codes
python extract_addresses.py --input ohio_comprehensive_sample.csv --zip 43215 45202 44114 --output major_cities.csv
```

### Filter by City (manual approach)

```bash
# Use grep to filter by city first, then by zip
grep "Columbus" ohio_comprehensive_sample.csv > columbus_only.csv
python extract_addresses.py --input columbus_only.csv --zip all --output columbus_addresses.csv
```

## Sample Data Statistics

```
Total Addresses: 566
Cities: 8
Zip Codes: 40

Addresses by City:
- Akron: 90
- Canton: 87
- Cleveland: 79
- Cincinnati: 74
- Toledo: 64
- Columbus: 64
- Dayton: 58
- Youngstown: 50
```

## Available Zip Codes in Sample Data

### Columbus (64 addresses)
- 43201, 43206, 43214, 43215, 43229

### Cleveland (79 addresses)
- 44102, 44103, 44113, 44114, 44115

### Cincinnati (74 addresses)
- 45202, 45203, 45214, 45219, 45229

### Toledo (64 addresses)
- 43604, 43606, 43607, 43608, 43609

### Akron (90 addresses)
- 44308, 44310, 44311, 44313, 44314

### Dayton (58 addresses)
- 45402, 45403, 45404, 45405, 45406

### Youngstown (50 addresses)
- 44503, 44504, 44505, 44506, 44507

### Canton (87 addresses)
- 44702, 44703, 44705, 44706, 44707

## Getting Real Statewide Ohio Data

### The Challenge

Complete statewide Ohio address data (5-7 million records) is not freely available as a single CSV download. The data is decentralized across 88 counties.

### Recommended Solutions

1. **OpenAddresses (batch.openaddresses.io)**
   - Register for free account
   - Download by county
   - Merge datasets

2. **County GIS Websites**
   - Major counties provide free downloads
   - Check individual county auditor/GIS sites

3. **Ohio OGRIP Portal**
   - ogrip-geohio.opendata.arcgis.com
   - Regional datasets available
   - CSV export option

See **OHIO_ADDRESS_DATA_GUIDE.md** for detailed instructions.

## Example Workflows

### Workflow 1: Filter Columbus Downtown

```bash
python extract_addresses.py \
  --input ohio_comprehensive_sample.csv \
  --zip 43215 \
  --output columbus_downtown.csv
```

### Workflow 2: Extract Multiple Cities

```bash
# Columbus and Cincinnati
python extract_addresses.py \
  --input ohio_comprehensive_sample.csv \
  --zip 43215 43206 45202 45203 \
  --output columbus_cincinnati.csv
```

### Workflow 3: Process Real County Data

```bash
# Assuming you downloaded Franklin County data
python extract_addresses.py \
  --input franklin_county.csv \
  --zip all \
  --output franklin_processed.csv

# Filter for specific zip codes
python extract_addresses.py \
  --input franklin_county.csv \
  --zip 43215 43214 \
  --output franklin_filtered.csv
```

## Data Format

All CSV files use this structure:

```csv
number,street,city,state,postcode,latitude,longitude
100,High St,Columbus,OH,43215,39.9612,-82.9988
```

## Requirements

```bash
pip install -r requirements.txt
```

Dependencies:
- pandas
- requests
- tqdm

## Notes on Sample Data

The included sample data (`ohio_comprehensive_sample.csv`) is **synthetic/representative data** generated for demonstration purposes. It:

- Uses realistic Ohio city names and zip codes
- Contains plausible street names and address numbers
- Includes approximate coordinates for each city
- Represents the data structure you'll find in real datasets

For production use, obtain real data using the methods described in **OHIO_ADDRESS_DATA_GUIDE.md**.

## Support

For issues or questions:
1. Check **OHIO_ADDRESS_DATA_GUIDE.md** for data sources
2. Review script help: `python extract_addresses.py --help`
3. Verify input file format matches expected structure

## License

Scripts are open-source. Data sources have their own licenses - please review before use.
