# Ohio Statewide Address Data Extraction Guide

## Current Situation

Complete statewide Ohio address data is **not freely available as a single CSV download** from open-source sites as of 2025. Here's why and what alternatives exist:

### Why Statewide Data Isn't Readily Available

1. **OpenAddresses Changes**: OpenAddresses moved to batch.openaddresses.io which requires authentication and now primarily provides GeoJSON format
2. **Decentralized Data**: Ohio address data is managed at the county level, not as a single statewide dataset
3. **Data Size**: Statewide address data for Ohio contains millions of records and is typically too large for simple downloads
4. **Access Restrictions**: Most comprehensive sources now require API tokens or accounts

## Available Options

### Option 1: County-by-County Download (FREE)

Ohio has 88 counties. Many counties provide free address data:

#### Known Free Sources:

**Cuyahoga County** (Cleveland area)
- Portal: https://myplace.cuyahogacounty.gov/
- Format: CSV download available
- Coverage: Cuyahoga County addresses

**Franklin County** (Columbus area)
- Check Franklin County Auditor or GIS website
- May require registration

**Hamilton County** (Cincinnati area)
- Check Hamilton County GIS website

**Lucas County** (Toledo area)
- GIS Services available at lcenggis.co.lucas.oh.us

### Option 2: OpenAddresses via batch.openaddresses.io (FREE with registration)

1. Visit: https://batch.openaddresses.io/
2. Create a free account
3. Download Ohio data by county or region
4. Format: GeoJSON (can be converted to CSV)

**Conversion Command:**
```bash
# Using ogr2ogr (from GDAL)
ogr2ogr -f CSV ohio_addresses.csv ohio_addresses.geojson

# Using jq
jq -r '.features[] | [.properties.number, .properties.street, .properties.city, .properties.postcode] | @csv' input.geojson > output.csv
```

### Option 3: Ohio OGRIP Portal (Registration may be required)

- Portal: https://ogrip-geohio.opendata.arcgis.com/
- Data: Address Points, Parcels, Boundaries
- Formats: CSV, GeoJSON, Shapefile, KML
- Coverage: Various regions (mostly county-level)

### Option 4: Commercial Data Services

For complete statewide coverage:
- **Regrid**: https://regrid.com/ (paid, but comprehensive)
- **SafeGraph**: Address and POI data (paid)
- **Data Axle**: Business and residential addresses (paid)

### Option 5: OpenStreetMap (FREE, but incomplete)

OpenStreetMap contains many Ohio addresses but is not comprehensive:

```bash
# Download Ohio OSM data
wget https://download.geofabrik.de/north-america/us/ohio-latest.osm.pbf

# Extract addresses using osmium or osm2pgsql
osmium tags-filter ohio-latest.osm.pbf nwr/addr:housenumber -o ohio-addresses.osm.pbf
```

## Recommended Approach for Complete State Coverage

### Strategy 1: Automated County Collection

1. Create a script that iterates through all 88 Ohio counties
2. Check each county's GIS/Auditor website for address data
3. Download available data
4. Merge into single dataset

### Strategy 2: Use OpenAddresses Batch

1. Register at batch.openaddresses.io
2. Download all available Ohio county data
3. Convert GeoJSON to CSV
4. Merge all county files

### Strategy 3: Hybrid Approach

1. Get bulk data from OpenAddresses for counties that have it
2. Fill gaps with individual county downloads
3. Merge and deduplicate

## Ohio Counties List

The state has 88 counties. Major counties by population:

1. Cuyahoga (Cleveland) - ~1.2M people
2. Franklin (Columbus) - ~1.3M people
3. Hamilton (Cincinnati) - ~830K people
4. Summit (Akron) - ~540K people
5. Montgomery (Dayton) - ~530K people
6. Lucas (Toledo) - ~430K people
7. Butler - ~390K people
8. Stark (Canton) - ~370K people
9. Lorain - ~310K people
10. Mahoning (Youngstown) - ~230K people

[... 78 more counties]

## Estimated Data Size

- **Statewide addresses**: 5-7 million records
- **CSV file size**: 500MB - 1.5GB (uncompressed)
- **Download time**: Varies by source and connection

## Using the Scripts in This Repository

### For Individual County Data

```bash
# If you have a CSV file from a county
python extract_addresses.py --input county_data.csv --zip 43215 --output filtered.csv
```

### For ArcGIS REST Services

```bash
# Download from an ArcGIS service
python download_ohio_addresses.py --url "https://services.../FeatureServer/0" --output addresses.csv
```

### For Bulk Processing

```bash
# Process multiple county files
for file in counties/*.csv; do
    python extract_addresses.py --input "$file" --zip all --output "processed/$(basename $file)"
done

# Merge all processed files
cat processed/*.csv > ohio_all_addresses.csv
```

## Next Steps

To get complete Ohio address data, I recommend:

1. **Immediate**: Register at batch.openaddresses.io and download available counties
2. **Supplemental**: Visit major county GIS websites for direct downloads
3. **Processing**: Use the scripts in this repo to filter and merge data

## Additional Resources

- **Ohio OGRIP**: https://ogrip.oit.ohio.gov/
- **OpenAddresses GitHub**: https://github.com/openaddresses/openaddresses
- **TIGER/Line (Census)**: https://www.census.gov/geographies/mapping-files/time-series/geo/tiger-line-file.html
  - Note: TIGER data has street ranges, not individual addresses

## Need Help?

If you need assistance:
1. Specify which counties you need most urgently
2. I can help create scripts to download from specific county sources
3. I can help with data merging and deduplication once you have the files

---

**Last Updated**: 2025-10-20
