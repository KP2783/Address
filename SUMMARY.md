# Address Data Processing Summary

## Overview
Successfully processed and validated real address data from Franklin and Delaware Counties, Ohio.

## Data Source
- **Original Data**: GeoJSON files from the `oh/` folder
  - `franklin-addresses-county.geojson` (228 MB)
  - `delaware-addresses-county.geojson` (31 MB)

## Processing Results

### Total Addresses Processed: **968,278**
- ✓ **Valid Addresses: 959,295 (99.1%)**
- ✗ Invalid Addresses: 8,983 (0.9%)

### County Breakdown

#### Franklin County
- **Valid Addresses: 849,161**
- Original records: 852,412
- Validation rate: 99.6%
- Major cities included: Columbus, Dublin, Hilliard, Upper Arlington, Westerville, Grove City, Reynoldsburg, Gahanna, Worthington, Whitehall, Bexley, and more

#### Delaware County
- **Valid Addresses: 110,134**
- Original records: 115,866
- Validation rate: 95.1%
- Major cities included: Delaware, Powell, Sunbury, Lewis Center, Galena, Westerville (partial)

## Output Files

> All output files below live in [`shared/data/`](shared/data/).

### 1. addresses.txt (38 MB)
**Format**: Human-readable text file with clean addresses
**Content**: One address per line in standard format
```
[House Number], [Street Name], [Unit], [City], [State], [Zip Code]
```
**Example**:
```
3106, SOMERFORD RD, Upper Arlington, OH, 43221
4618, EASTWAY CT, APT A, Whitehall, OH, 43213
```

### 2. addresses_with_coords.txt (70 MB)
**Format**: Text file with addresses and GPS coordinates
**Content**: Addresses with latitude/longitude
```
[Full Address] | Lat: [Latitude], Lon: [Longitude]
```
**Example**:
```
3106, SOMERFORD RD, Upper Arlington, OH, 43221 | Lat: 40.019781, Lon: -83.063655
```

### 3. addresses_clean.csv (61 MB)
**Format**: Comma-separated values (CSV) - importable to Excel, databases, etc.
**Columns**:
- number (house number)
- street (street name)
- unit (apartment/unit number if applicable)
- city (city name)
- region (state code - OH)
- postcode (5-digit zip code)
- district (county district code)
- latitude (GPS coordinate)
- longitude (GPS coordinate)

## Data Quality

### Validation Checks Performed
1. ✓ House number present
2. ✓ Street name present
3. ✓ City name present
4. ✓ Valid 5-digit zip code format
5. ✓ Valid GPS coordinates
6. ✓ Coordinates within Ohio boundaries

### Data Cleaning Applied
1. Standardized street names (uppercase)
2. Removed extra spaces
3. Standardized city names (title case)
4. Validated zip code format
5. Ensured proper unit/apartment formatting

### Common Validation Issues Found
- Missing city names (< 1%)
- Missing house numbers (< 1%)
- Missing street names (< 1%)
- Invalid coordinates (< 0.1%)

## Usage Recommendations

### Best File for Your Use Case

**For Basic Mailing Lists:**
- Use: `addresses.txt`
- Simple, clean format
- Easy to read and import

**For Mapping/GIS Applications:**
- Use: `addresses_with_coords.txt` or `addresses_clean.csv`
- Includes GPS coordinates
- Can be plotted on maps

**For Database Import:**
- Use: `addresses_clean.csv`
- Structured columns
- Easy to import into Excel, SQL, or CRM systems

## Data Statistics

### Franklin County Coverage
- Total Zip Codes: 60+
- Major Cities: 15+
- Total Valid Addresses: 849,161

### Delaware County Coverage
- Total Zip Codes: 10+
- Major Cities: 8+
- Total Valid Addresses: 110,134

### Combined Dataset
- **Total Valid Addresses: 959,295**
- Total Counties: 2
- Total Zip Codes: 70+
- Total Cities/Townships: 25+

## Next Steps

1. **Review the data**: Open `shared/data/addresses.txt` or `shared/data/addresses_clean.csv` to review
2. **Import into your system**: Use the CSV file for database/CRM import
3. **Filter as needed**: The CSV can be filtered by city, zip code, or district
4. **Map the data**: Use coordinates for geographical analysis

## Script Used
- **Script**: [clean_and_validate_addresses.py](shared/scripts/clean_and_validate_addresses.py)
- **Language**: Python 3
- **Dependencies**: json, csv, re, pathlib
- **Processing Time**: ~2-3 minutes
- **Memory Usage**: Efficient line-by-line processing

## Notes

- All addresses are from public GeoJSON data sources
- Addresses have been validated and cleaned for quality
- GPS coordinates are included for mapping applications
- Data is current as of the source file dates (October 2024)
- Invalid addresses were excluded from output files

---

**Generated**: October 20, 2025
**Total Processing Time**: ~3 minutes
**Success Rate**: 99.1%
