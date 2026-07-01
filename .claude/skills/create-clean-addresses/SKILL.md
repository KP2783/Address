---
name: create-clean-addresses
description: Produce a clean, validated, residential-only address CSV for a central-Ohio ZIP code from county GeoJSON source data. Use when the user wants to generate clean addresses for a ZIP code (e.g. "create clean addresses for 43232", "process zip 43147"). Encodes the proven pipeline from the 43213/43229 projects with the cost lessons applied (parcel-first, no enableUspsCass).
---

# Create Clean Addresses for a ZIP Code

Produce a final `addresses_<ZIP>_residential_final.csv` — residential-only, parcel-enriched, optionally validated — for a central-Ohio ZIP code. Based on the proven 43213/43229 reference pipeline, with the **learned cost lessons applied** (parcel data first; never `enableUspsCass`).

## What you produce
One deliverable per ZIP: `<ZIP>_project/data/addresses_<ZIP>_residential_final.csv`

Column schema (from `43213_project` reference):
```
address, number, street, unit, city, state, zip,
latitude, longitude,
final_classification, classification_source,
google_validated_address, google_classification, google_city,   # only if Google run
parcel_id, land_use_code, land_use_type, occupancy,
owner_name, homestead, year_built, bedrooms, bathrooms,
appraised_value, annual_tax, sale_price, sale_date
```

## ⚠️ Cost-safety rules (read first — these came from a $258 mistake)
1. **Classify residential with parcel data FIRST.** It's free. Only addresses parcel data cannot classify should go to a paid API.
2. **Filter out commercial with parcel data BEFORE calling any paid API.**
3. **NEVER set `enableUspsCass: true` on Google.** It double-bills every call ($0.005 → $0.01). The 43213 run set it (`43213_project/scripts/validate_google_43213.py:71`) and cost $258.98 instead of ~$101. Omit the field or set `false` — `metadata.residential` works without it.
4. **Set a Google Cloud billing budget/alert before any bulk Google call.**
5. Prefer **Smarty** over Google when a paid validator is needed (no CASS surcharge, returns `metadata.residential`).

## Data sources (all already present in the repo)
- **Raw addresses:** `oh/franklin-addresses-county.geojson` (228 MB) — contains all central-Ohio target ZIPs. Postcode field is `"postcode": "XXXXX"` (note the space).
- **Overlap warning:** `oh/city_of_columbus-addresses-city.geojson` duplicates the Columbus addresses in the Franklin file ~1:1. **Do not merge the two** — pick `franklin-addresses-county.geojson` as the single source to avoid duplicate rows.
- **Parcels (residential classifier):** `shared/data/franklin_county_parcels.csv` (250 MB) — Franklin County auditor parcel data. Raw columns are **uppercase auditor codes**: `LANDUSE`, `HOMSTD` (homestead / owner-occupied), `YEARBLT`, `APPRBLD` (building appraisal), `OWNER_ADD1` vs `STADDR` (owner-mailing vs property address), `TRANDT`/`PRICE` (last sale). `match_parcels_43213.py` maps these to lowercase `land_use_code` / `homestead` / `year_built` / `occupancy` in its output. This CSV is a **snapshot (~Mar 2025)** — use the live auditor portal below for current status.
- **Franklin County Auditor — live property search (free, authoritative):** the *same* data as the parcel CSV, but live/current. Use it to confirm an address is real and to resolve owner / homestead / occupancy where the snapshot is stale or `UNKNOWN`. Best for spot-checks and the risk list, **not** bulk.
  - Portal home / owner search: `https://property.franklincountyauditor.com/`
  - Address search: `https://property.franklincountyauditor.com/_web/search/commonsearch.aspx?mode=address`
  - Parcel-ID search (no dashes): `https://property.franklincountyauditor.com/_web/search/commonsearch.aspx?mode=parid`
  - Fetch a property card into the run with `mcp__web_reader__webReader` when needed.
- **Reference implementation:** `43213_project/` (cleanest end-to-end example).

## Legitimacy & occupancy verification (free, no Google)
The **default** validation path uses no paid API. Treat the two questions separately:

**Legitimacy — is the address real?** (free, reliable):
- **Parcel match** — a row that joins to a `PARCEL ID` is a real, taxed property.
- **Census Geocoder** (`43229_project/scripts/validate_43229_with_units.py`) — free existence/coordinate check.
- **Franklin County Auditor live search** (URLs above) — authoritative per-address lookup.

**Occupancy — is it lived-in?** No free source is definitive per-address; build a composite score from parcel fields and flag the rest for spot-check:
- `classify_occupancy()` in `match_parcels_43213.py:46` already returns `OWNER_OCCUPIED` (`HOMSTD='Y'`), `LIKELY_OWNER` / `LIKELY_RENTAL` (owner-vs-property address match), or `UNKNOWN` — the first three imply **occupied**.
- Require `APPRBLD > 0` (a structure exists) and `YEARBLT > 0`; **exclude `LANDUSE` 500/501/503 (RESIDENTIAL_VACANT)**.
- `classify_land_use()` (line 72) separates residential (`510/511/520/530/550–560`) from commercial (`4xx`), industrial (`3xx`), exempt (`6/7/8xx`).
- For `UNKNOWN` or stale parcels, verify current owner + homestead via the **Franklin County Auditor live search**.
- Label each row `OCCUPIED` / `VACANT` / `UNKNOWN`.

**Web search (free, sampling only — NOT for bulk):** `WebSearch` (US) + `mcp__web_reader__webReader` for spot-checking a random sample and resolving the risk/`UNKNOWN` list against the auditor site, Zillow/Redfin, OSM.

## Target ZIPs and source selection
| ZIP | Default city | Source | Boundary handling |
|---|---|---|---|
| 43232 | Columbus | franklin | — |
| 43227 | Columbus | franklin | — |
| 43207 | Columbus | franklin | — |
| 43224 | Columbus | franklin | — |
| 43211 | Columbus | franklin | — |
| 43004 | Blacklick | franklin | — |
| 43125 | Grove City | franklin | — |
| 43110 | Canal Winchester | franklin **+ fairfield** | merge `oh/fairfield-addresses-county.geojson`, dedup |
| 43147 | Pickerington | franklin **+ fairfield** | merge `oh/fairfield-addresses-county.geojson`, dedup (Fairfield has ~18k of this ZIP) |

## Procedure (parameterize `$ZIP`, `$CITY`, `$SOURCES`)

### Step 0 — Scaffold the project
Create `<ZIP>_project/` mirroring the reference layout: `data/`, `output/`, `review/`, `scripts/`.
Copy the reference scripts from `43213_project/scripts/` and replace the ZIP literal and default city throughout:
```
mkdir -p <ZIP>_project/{data,output,review,scripts}
cp 43213_project/scripts/*.py <ZIP>_project/scripts/
# then, in each copied script, replace the 43213 literal and the default city:
#   '43213' -> '<ZIP>',  'Columbus' -> '<CITY>'  (only the default-city assignment)
```
> Note: these scripts hard-code paths like `/Users/kevinpatel/Address/43213_project/...`, so the find-and-replace must cover the project directory name too (`43213_project` → `<ZIP>_project`). Until the Stage-3 refactor parameterizes paths, this copy-and-replace pattern is the working approach.

### Step 1 — Extract from GeoJSON, filter to ZIP
Reference: `43068_project/scripts/extract_43068.py` / `shared/scripts/extract_addresses.py`
- Stream `oh/franklin-addresses-county.geojson`, keep features where `"postcode" == "<ZIP>"`.
- For boundary ZIPs (43110, 43147): also stream `oh/fairfield-addresses-county.geojson` and concatenate.
- Normalize, **dedup** on (number, street, unit), drop rows missing number/street/city or with invalid 5-digit postcode / out-of-Ohio coords.
- Output: `<ZIP>_project/data/addresses_<ZIP>.csv`

### Step 2 — Format / normalize
Reference: `43213_project/scripts/filter_residential_43213.py`
- Uppercase street names, collapse whitespace, Title-case city, validate postcode format, normalize unit (`APT`/`STE`/`#`).
- Output: `<ZIP>_project/data/addresses_<ZIP>_formatted.csv`

### Step 3 — Enrich with parcels (this is the free residential classifier)
Reference: `43213_project/scripts/match_parcels_43213.py`
- Join `shared/data/franklin_county_parcels.csv` on normalized house+street key; handle address ranges (e.g. `4019 - 4021 ABBEY CT`).
- Adds: `parcel_id, land_use_code, land_use_type, occupancy, owner_name, homestead, year_built, bedrooms, bathrooms, appraised_value, annual_tax, sale_price, sale_date`.
- Output: `<ZIP>_project/data/addresses_<ZIP>_enriched.csv`

### Step 4 — Residential classification (PRIMARY, free, do this first)
Classify by `land_use_code`. **Residential codes (Franklin County auditor):**
- `500, 501, 503` — residential vacant land
- `510, 511` — single-family
- `520, 530` — two-family / three-family
- `550, 551, 552, 553, 559, 560` — apartments
- Keep rows whose `land_use_code` ∈ this set; flag the rest commercial.
- Output: `addresses_<ZIP>_residential.csv` (parcel-classified) and a commercial-removal side file.

### Step 5 — Validate only what parcel data couldn't classify (paid APIs are OPTIONAL)
Run only on the ambiguous/residual set, never the whole ZIP.
- **Smarty (preferred if paid validator needed):**
  - Endpoint `https://us-street.api.smarty.com/street-address`, auth env `AUTH_ID` / `AUTH_TOKEN`.
  - Params: `{"street", "city", "state", "zipcode", "match": "invalid"}`.
  - Residential field: `metadata.residential` / `metadata.rdi`.
  - Reference: `43213_project/scripts/validate_smarty_43213.py`, `43026_project/scripts/validate_smarty_smart.py`.
- **Google (only if Smarty unavailable, and ONLY for the small residual set):**
  - Endpoint `https://addressvalidation.googleapis.com/v1:validateAddress`, auth env `GOOGLE_API_KEY`.
  - **Set `"enableUspsCass": false` or omit it.** Do NOT copy line 71 of `validate_google_43213.py`.
  - Residential: `metadata.residential` / `metadata.business`; fallback `uspsData.addressRecordType` (S/H/R = residential, F/G/P = commercial).
  - Set a billing alert first. Reference (fix the flag before reuse): `43213_project/scripts/validate_google_43213.py`.
- **Free fallback (no residential classification, geocoding only):** Census `https://geocoding.geo.census.gov/geocoder/locations/onelineaddress` — reference `43229_project/scripts/validate_43229_with_units.py`. Use to confirm an address exists / get coords, not to classify.

### Step 6 — Manual review of risk categories
Surface these for human review (do not auto-delete):
- **Units/apartments** — verify residential (see `shared/review/risk_units.txt`).
- **Commercial corridors** — known mixed-use streets (see `shared/review/commercial_corridor_review.txt`, `removed_commercial_blvds.csv`).
- **Ambiguous / risk list** — `shared/review/risk_review_list.txt`, `review_streets_proactive.txt`.
- **Resolve via auditor** — verify current owner/homestead/occupancy for risk and `UNKNOWN` rows using the **Franklin County Auditor live search** (see *Legitimacy & occupancy verification* above); fetch property cards with `mcp__web_reader__webReader`.
- Output review lists under `<ZIP>_project/review/`.

### Step 7 — Merge & finalize
Reference: `43213_project/scripts/merge_final_43213.py`
- Merge parcel enrichment + any validation result; apply classification priority: **validation result → parcel land_use_code → default residential for matched apartments**.
- Write final deliverable with the schema above.
- Output: `<ZIP>_project/data/addresses_<ZIP>_residential_final.csv`

### Step 8 — Verify
- Row count is plausible for the ZIP (see counts table below; expect rough parity with source postcode counts).
- No row lacks `number`/`street`/`city`/`zip` or has an out-of-Ohio coordinate.
- Spot-check 10 rows: classification matches parcel `land_use_type`.
- No `enableUspsCass` anywhere in the run (`grep -rn enableUspsCass <ZIP>_project/` must be empty or show `false`).

## Expected scale (source postcode occurrence counts, for sanity-checking Step 1 output)
| ZIP | franklin count | (+ fairfield) |
|---|---|---|
| 43232 | ~24.8k | — |
| 43207 | ~25.6k | — |
| 43224 | ~20.4k | — |
| 43110 | ~22.4k | +~3.6k |
| 43147 | ~18.1k | +~18.3k |
| 43227 | ~11.6k | — |
| 43211 | ~12.0k | — |
| 43004 | ~12.3k | — |
| 43125 | ~7.6k | — |

(Counts are raw GeoJSON feature occurrences before dedup; your final residential count will be lower after dedup + commercial removal + residential filter.)

## Reference script index
| Stage | Reference script | Notes |
|---|---|---|
| Extract | `43068_project/scripts/extract_43068.py`, `shared/scripts/extract_addresses.py` | stream GeoJSON, filter postcode, dedup |
| Format/filter | `43213_project/scripts/filter_residential_43213.py` | normalize + commercial keyword filter |
| Parcel enrich | `43213_project/scripts/match_parcels_43213.py` | join `shared/data/franklin_county_parcels.csv` |
| Validate (Smarty) | `43213_project/scripts/validate_smarty_43213.py` | preferred paid validator |
| Validate (Google) | `43213_project/scripts/validate_google_43213.py` | ⚠️ fix `enableUspsCass` before reuse |
| Validate (free) | `43229_project/scripts/validate_43229_with_units.py` | Census geocoder, no classification |
| Merge/finalize | `43213_project/scripts/merge_final_43213.py` | classification priority logic |
| Commercial removal | `shared/scripts/remove_specific_commercial.py`, `remove_reviewed_addresses.py` | reads `_formatted.csv`, writes `_cleaned.csv` |

## When invoked
Ask the user to confirm: the target ZIP(s), whether paid validation (Smarty/Google) is authorized for this run, and that a Google billing alert is set if Google will be used. Default to **parcel-only classification** (no paid API) unless they opt in.
