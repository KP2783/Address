# Franklin and Delaware Counties, Ohio - Address Data Guide

## Overview

This guide provides information on accessing real address data for Franklin County and Delaware County, Ohio.

## Sample Data Provided

This repository includes **comprehensive sample data** for both counties:

### Franklin County Sample Data
- **File**: `franklin_county_addresses.csv`
- **Addresses**: 1,110 addresses
- **Cities**: Columbus, Westerville, Grove City, Gahanna, Reynoldsburg
- **Zip Codes**: 36 different zip codes
- **Major Zip Codes**:
  - 43230 (Gahanna area): 101 addresses
  - 43123 (Grove City): 99 addresses
  - 43081, 43082 (Westerville): 131 addresses
  - 43215 (Downtown Columbus): 27 addresses

### Delaware County Sample Data
- **File**: `delaware_county_addresses.csv`
- **Addresses**: 600 addresses
- **Cities**: Delaware, Lewis Center, Powell, Sunbury, Galena
- **Zip Codes**: 5 different zip codes
  - 43015 (Delaware): 200 addresses
  - 43065 (Powell): 120 addresses
  - 43035 (Lewis Center): 150 addresses
  - 43074 (Sunbury): 80 addresses
  - 43021 (Galena): 50 addresses

### Combined Data
- **File**: `franklin_delaware_combined.csv`
- **Total Addresses**: 1,710
- **Total Cities**: 10
- **Total Zip Codes**: 41

## Quick Start with Sample Data

### Extract All Addresses
```bash
# Franklin County
python extract_addresses.py --input franklin_county_addresses.csv --zip all --output franklin_all.csv

# Delaware County
python extract_addresses.py --input delaware_county_addresses.csv --zip all --output delaware_all.csv
```

### Extract Specific Zip Codes

```bash
# Downtown Columbus (43215)
python extract_addresses.py --input franklin_county_addresses.csv --zip 43215 --output columbus_downtown.csv

# Delaware city (43015)
python extract_addresses.py --input delaware_county_addresses.csv --zip 43015 --output delaware_city.csv

# Powell (43065)
python extract_addresses.py --input delaware_county_addresses.csv --zip 43065 --output powell.csv

# Multiple Columbus area zip codes
python extract_addresses.py --input franklin_county_addresses.csv --zip 43215 43201 43206 43214 --output columbus_central.csv
```

### Extract from Combined File

```bash
# Get addresses from both counties for specific zips
python extract_addresses.py --input franklin_delaware_combined.csv --zip 43215 43015 43065 --output multi_county.csv
```

## Accessing Real Data from Official Sources

### Franklin County (1.3 million people)

#### Option 1: City of Columbus Open Data Portal (RECOMMENDED)
**Best for**: Central Ohio / Columbus area addresses

- **Portal**: https://data-columbus.opendata.arcgis.com/
- **Dataset**: "Address Points"
- **URL**: https://data-columbus.opendata.arcgis.com/datasets/0daacee16537420fab4a55ce4806d538_0
- **Coverage**: Addressable structures in central Ohio (Columbus metro area)
- **Format**: CSV, GeoJSON, Shapefile, KML
- **Free**: Yes
- **Update Frequency**: Regular updates

**How to Download**:
1. Visit the Address Points dataset page
2. Click "Download" button
3. Select "CSV" format
4. Extract the downloaded file
5. Use with the scripts in this repository

#### Option 2: Franklin County Auditor Open Data
**Best for**: Parcel-based address data

- **Portal**: https://auditor-fca.opendata.arcgis.com/
- **Data Types**: Parcels, boundaries, administrative data
- **Format**: Multiple formats including CSV
- **Free**: Yes

**Note**: The auditor's portal focuses on parcel data. For point-level addresses, use Columbus Open Data.

#### Option 3: MORPC (Mid-Ohio Regional Planning Commission)
**Best for**: Regional data including multiple counties

- **Portal**: https://public-morpc.hub.arcgis.com/
- **Coverage**: Multi-county regional data
- **Format**: Various GIS formats

### Delaware County (200,000+ people)

#### Option 1: Delaware County GIS Data Download Hub (RECOMMENDED)
**Best for**: Official county address data

- **Portal**: https://gisdata-delco.hub.arcgis.com/
- **Dataset**: "E911 Address Points"
- **Coverage**: All certified addresses in Delaware County
- **Format**: CSV, GeoJSON, Shapefile, KML
- **Free**: Yes
- **Update**: 3rd of each month
- **Maintained by**: Delaware County Auditor's GIS Office

**How to Download**:
1. Visit https://gisdata-delco.hub.arcgis.com/
2. Search for "Address Points" or "E911"
3. Click on the dataset
4. Click "Download" and select CSV format
5. Use with extraction scripts

**Direct Link to E911 Data**:
- https://gisdata-delco.hub.arcgis.com/maps/319c975ff74d465abf8df89c3f4e6ef2

#### Option 2: Delaware County Auditor GIS
**Portal**: https://gis.co.delaware.oh.us/
**Data**: Parcels, roads, boundaries, addresses

#### Option 3: Delaware County MapServer API
**For Developers**:
- **API Endpoint**: https://maps.delco-gis.org/arcgiswebadaptor/rest/services/DelawareCountyData/MapServer
- **Format**: JSON (ArcGIS REST API)
- **Use**: Can query programmatically using `download_ohio_addresses.py` script

### Using Our Scripts with Real Data

Once you download real data from the sources above:

```bash
# After downloading Columbus address points as columbus_real.csv
python extract_addresses.py --input columbus_real.csv --zip 43215 --output downtown.csv

# After downloading Delaware County E911 data as delaware_real.csv
python extract_addresses.py --input delaware_real.csv --zip 43015 --output delaware_city.csv

# Filter by multiple zip codes
python extract_addresses.py --input columbus_real.csv --zip 43201 43206 43215 43214 --output central_columbus.csv
```

## Data Size Expectations (Real Data)

### Franklin County (Real Data)
- **Estimated Addresses**: 400,000 - 600,000
- **CSV File Size**: 50-100 MB (uncompressed)
- **Download Time**: 2-10 minutes depending on connection

### Delaware County (Real Data)
- **Estimated Addresses**: 80,000 - 100,000
- **CSV File Size**: 10-20 MB (uncompressed)
- **Download Time**: 1-3 minutes

## Common Zip Codes Reference

### Franklin County Major Zip Codes

**Downtown Columbus**
- 43215 - Downtown core
- 43201 - Short North, Victorian Village
- 43206 - German Village, Brewery District
- 43215 - Arena District, Discovery District

**Columbus Neighborhoods**
- 43202 - Clintonville
- 43214 - North Columbus
- 43229 - Northeast Columbus
- 43235 - Northwest Columbus (Worthington border)

**Suburbs**
- 43081, 43082 - Westerville
- 43230 - Gahanna
- 43123 - Grove City
- 43068 - Reynoldsburg

### Delaware County Major Zip Codes

- 43015 - Delaware (county seat)
- 43065 - Powell
- 43035 - Lewis Center
- 43074 - Sunbury
- 43021 - Galena

## Alternative Data Sources

### OpenAddresses
1. Visit https://batch.openaddresses.io/
2. Create free account
3. Search for "Ohio" and filter by Franklin or Delaware
4. Download GeoJSON files
5. Convert to CSV using:
   ```bash
   ogr2ogr -f CSV output.csv input.geojson
   ```

### U.S. Census TIGER/Line Files
- **URL**: https://www.census.gov/geographies/mapping-files/time-series/geo/tiger-line-file.html
- **Data**: Address ranges (not individual addresses)
- **Format**: Shapefile
- **Coverage**: Nationwide

## Script Reference

### Extract by Zip Code
```bash
python extract_addresses.py --input <file.csv> --zip <zip1> <zip2> ... --output <output.csv>
```

### Download from ArcGIS API
```bash
python download_ohio_addresses.py --url <FeatureServer URL> --output <output.csv>
```

### Example Workflows

**Workflow 1: Get all Columbus downtown addresses**
```bash
# Use sample data
python extract_addresses.py --input franklin_county_addresses.csv --zip 43215 --output downtown.csv

# Or download real data first from Columbus Open Data portal, then:
python extract_addresses.py --input columbus_addresses_real.csv --zip 43215 --output downtown_real.csv
```

**Workflow 2: Get all Delaware County addresses**
```bash
# Use sample data
python extract_addresses.py --input delaware_county_addresses.csv --zip all --output delaware_all.csv

# Or download from Delaware County GIS hub, then:
python extract_addresses.py --input delaware_e911_real.csv --zip all --output delaware_all_real.csv
```

**Workflow 3: Combine specific cities**
```bash
# Columbus downtown + Delaware city + Powell
python extract_addresses.py --input franklin_delaware_combined.csv --zip 43215 43015 43065 --output selected_cities.csv
```

## Data Quality Notes

### Sample Data (Included)
- ✓ Realistic structure and format
- ✓ Representative zip codes
- ✓ Good for testing and development
- ✗ Not actual real-world addresses
- ✗ Limited coverage

### Real Data (From Official Sources)
- ✓ Actual real-world addresses
- ✓ Complete coverage
- ✓ Regularly updated
- ✓ Authoritative source
- ✓ Production-ready

## Support and Updates

**For Real Data Issues**:
- Franklin County: Contact Columbus Open Data or Franklin County Auditor
- Delaware County: Contact Delaware County GIS Office

**For Script Issues**:
- Check script help: `python extract_addresses.py --help`
- Review examples in README.md

## License and Usage

**Sample Data**: Provided for demonstration purposes
**Real Data**: Subject to respective county/city terms of use
**Scripts**: Open source

---

**Last Updated**: 2025-10-20
**Counties Covered**: Franklin, Delaware
**Data Type**: Address Points
