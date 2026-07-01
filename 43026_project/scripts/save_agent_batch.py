
import csv

# Define the batch data locally
batch_data = [
    {
        "address": "2422 BAYSIDE DR, Columbus, OH, 43026",
        "result": """The property at 2422 Bayside Dr... is likely an apartment...
        Source: search_inference"""
    },
    {
        "address": "2422 CRYSTAL SPRINGS DR, Columbus, OH, 43026",
        "result": """The property at 2422 Crystal Springs Dr... is a condominium...
        Source: zillow.com"""
    },
    {
        "address": "2422 HILLIARD PARK BLVD, Columbus, OH, 43026",
        "result": """The property at 2422 Hilliard Park Blvd... is part of the Hilliard Park Apartments...
        Source: irtliving.com"""
    },
    {
        "address": "2422 OAKTHORPE DR, Columbus, OH, 43026",
        "result": """The property at 2422 Oakthorpe Dr... is a single-family home...
        Source: zillow.com"""
    },
    {
        "address": "2422 QUARRY STONE DR, Columbus, OH, 43026",
        "result": """The property at 2422 Quarry Stone Dr... is a condo...
        Source: zillow.com"""
    },
    {
        "address": "2422 SPRING ROW LN, Columbus, OH, 43026",
        "result": """The property at 2422 Spring Row Ln... is a condo...
        Source: zillow.com"""
    },
    {
        "address": "2423 BAYSIDE DR, Columbus, OH, 43026",
        "result": """The property at 2423 Bayside Dr... is likely an apartment...
        Source: search_inference"""
    },
    {
        "address": "2423 LAKEBRIDGE LN, Columbus, OH, 43026",
        "result": """The property at 2423 Lakebridge Ln... is a condo...
        Source: zillow.com"""
    },
    {
        "address": "2423 SPRING ROW LN, Columbus, OH, 43026",
        "result": """The property at 2423 Spring Row Ln... is a condo...
        Source: zillow.com"""
    },
    {
        "address": "2423 SUMMERGREEN DR, Columbus, OH, 43026",
        "result": """The property at 2423 Summergreen Dr... is a condo...
        Source: zillow.com"""
    },
    {
        "address": "2423 WALBORN DR, Columbus, OH, 43026",
        "result": """The property at 2423 Walborn Dr... is a single-family home...
        Source: zillow.com"""
    },
    {
        "address": "2423 WARM SPRINGS DR, Columbus, OH, 43026",
        "result": """The property at 2423 Warm Springs Dr... is a condominium...
        Source: zillow.com"""
    },
    {
        "address": "2424 BAYSIDE DR, Columbus, OH, 43026",
        "result": """The property at 2424 Bayside Dr... is likely an apartment...
        Source: search_inference"""
    },
    {
        "address": "2424 HIGHLANDTOWN DR, Columbus, OH, 43026",
        "result": """The property at 2424 Highlandtown Dr... is a single-family home...
        Source: zillow.com"""
    },
    {
        "address": "2424 HILLIARD PARK BLVD, Columbus, OH, 43026",
        "result": """The property at 2424 Hilliard Park Blvd... is part of the Hilliard Park Apartments...
        Source: irtliving.com"""
    },
    {
        "address": "2424 MILLS FALL DR, Columbus, OH, 43026",
        "result": """The property at 2424 Mills Fall Dr... is a single-family residence...
        Source: douglasandassociatesrealty.com"""
    },
    {
        "address": "2424 PEARSON WAY, Columbus, OH, 43026",
        "result": """The property at 2424 Pearson Way... is a single-family home...
        Source: trulia.com"""
    },
    {
        "address": "2424 QUARRY STONE DR, Columbus, OH, 43026",
        "result": """The property at 2424 Quarry Stone Dr... is a condo...
        Source: zillow.com"""
    },
    {
        "address": "2424 SPRING ROW LN, Columbus, OH, 43026",
        "result": """The property at 2424 Spring Row Ln... is a condo...
        Source: zillow.com"""
    },
    {
        "address": "2424 STEWART HOLLOW CT, Columbus, OH, 43026",
        "result": """The property at 2424 Stewart Hollow Ct... is a "Single Family Residence"...
        Source: coldwellbankerhomes.com"""
    },
    {
        "address": "2424 SUMMERGREEN DR, Columbus, OH, 43026",
        "result": """The property at 2424 Summergreen Dr... is a condo...
        Source: zillow.com"""
    },
    {
        "address": "2424 WALBORN DR, Columbus, OH, 43026",
        "result": """The property at 2424 Walborn Dr... is a single-family home...
        Source: zillow.com"""
    },
    {
        "address": "2424 WARM SPRINGS DR, Columbus, OH, 43026",
        "result": """The property at 2424 Warm Springs Dr... is a condominium...
        Source: zillow.com"""
    },
    {
        "address": "2425 BAYSIDE DR, Columbus, OH, 43026",
        "result": """The property at 2425 Bayside Dr... is likely an apartment...
        Source: search_inference"""
    },
    {
        "address": "2425 LAKEBRIDGE LN, Columbus, OH, 43026",
        "result": """The property at 2425 Lakebridge Ln... is a condo...
        Source: realtor.com"""
    },
    {
        "address": "2425 SPRING ROW LN, Columbus, OH, 43026",
        "result": """The property at 2425 Spring Row Ln... is a condo...
        Source: zillow.com"""
    },
    {
        "address": "2425 STEWART HOLLOW CT, Columbus, OH, 43026",
        "result": """The property at 2425 Stewart Hollow Ct... is a single-family home...
        Source: zillow.com"""
    },
    {
        "address": "2425 SUMMERGREEN DR, Columbus, OH, 43026",
        "result": """The property at 2425 Summergreen Dr... is a condo...
        Source: zillow.com"""
    },
    {
        "address": "2425 WARM SPRINGS DR, Columbus, OH, 43026",
        "result": """The property at 2425 Warm Springs Dr... is a condominium...
        Source: zillow.com"""
    },
    {
        "address": "2426 BAYSIDE DR, Columbus, OH, 43026",
        "result": """The property at 2426 Bayside Dr... is likely an apartment...
        Source: search_inference"""
    },
    {
        "address": "2426 HILLIARD PARK BLVD, Columbus, OH, 43026",
        "result": """The property at 2426 Hilliard Park Blvd... is part of the Hilliard Park Apartments...
        Source: irtliving.com"""
    },
    {
        "address": "2426 QUARRY STONE DR, Columbus, OH, 43026",
        "result": """The property at 2426 Quarry Stone Dr... is a condo...
        Source: zillow.com"""
    },
    {
        "address": "2426 SPRING ROW LN, Columbus, OH, 43026",
        "result": """The property at 2426 Spring Row Ln... is a condo...
        Source: zillow.com"""
    },
    {
        "address": "2426 SUMMERGREEN DR, Columbus, OH, 43026",
        "result": """The property at 2426 Summergreen Dr... is a condo...
        Source: zillow.com"""
    },
    {
        "address": "2426 WARM SPRINGS DR, Columbus, OH, 43026",
        "result": """The property at 2426 Warm Springs Dr... is a condominium...
        Source: zillow.com"""
    },
    {
        "address": "2426 YAGGER BAY DR, Columbus, OH, 43026",
        "result": """The property at 2426 Yagger Bay Dr... is a single-family home...
        Source: zillow.com"""
    },
    {
        "address": "2427 BAYSIDE DR, Columbus, OH, 43026",
        "result": """The property at 2427 Bayside Dr... is likely an apartment...
        Source: search_inference"""
    },
    {
        "address": "2427 CRYSTAL SPRINGS DR, Columbus, OH, 43026",
        "result": """The property at 2427 Crystal Springs Dr... is a condominium...
        Source: zillow.com"""
    },
    {
        "address": "2427 LAKEBRIDGE LN, Columbus, OH, 43026",
        "result": """The property at 2427 Lakebridge Ln... is a condo...
        Source: realtor.com"""
    },
    {
        "address": "2427 OAKTHORPE DR, Columbus, OH, 43026",
        "result": """The property at 2427 Oakthorpe Dr... is a single-family home...
        Source: zillow.com"""
    },
    {
        "address": "2427 SPRING ROW LN, Columbus, OH, 43026",
        "result": """The property at 2427 Spring Row Ln... is a condo...
        Source: zillow.com"""
    },
    {
        "address": "2427 SUMMERGREEN DR, Columbus, OH, 43026",
        "result": """The property at 2427 Summergreen Dr... is a condo...
        Source: zillow.com"""
    },
    {
        "address": "2427 YAGGER BAY DR, Columbus, OH, 43026",
        "result": """The property at 2427 Yagger Bay Dr... is a single-family home...
        Source: zillow.com"""
    },
    {
        "address": "2428 CRYSTAL SPRINGS DR, Columbus, OH, 43026",
        "result": """The property at 2428 Crystal Springs Dr... is a condominium...
        Source: zillow.com"""
    },
    {
        "address": "2428 HILLIARD PARK BLVD, Columbus, OH, 43026",
        "result": """The property at 2428 Hilliard Park Blvd... is part of the Hilliard Park Apartments...
        Source: irtliving.com"""
    },
    {
        "address": "2428 OAKTHORPE DR, Columbus, OH, 43026",
        "result": """The property at 2428 Oakthorpe Dr... is a single-family home...
        Source: zillow.com"""
    },
    {
        "address": "2428 SUMMERGREEN DR, Columbus, OH, 43026",
        "result": """The property at 2428 Summergreen Dr... is a condo...
        Source: zillow.com"""
    },
    {
        "address": "2429 BAYSIDE DR, Columbus, OH, 43026",
        "result": """The property at 2429 Bayside Dr... is likely an apartment...
        Source: search_inference"""
    },
    {
        "address": "2429 CRYSTAL SPRINGS DR, Columbus, OH, 43026",
        "result": """The property at 2429 Crystal Springs Dr... is a condominium...
        Source: zillow.com"""
    },
    {
        "address": "2429 HIGHLANDTOWN DR, Columbus, OH, 43026",
        "result": """The property at 2429 Highlandtown Dr... is a Single Family home...
        Source: zillow.com"""
    },
    {
        "address": "2429 HILLIARD PARK BLVD, Columbus, OH, 43026",
        "result": """The property at 2429 Hilliard Park Blvd... is part of the Hilliard Park Apartments...
        Source: irtliving.com"""
    },
    {
        "address": "2429 SUMMERGREEN DR, Columbus, OH, 43026",
        "result": """The property at 2429 Summergreen Dr... is a condo...
        Source: zillow.com"""
    },
    {
        "address": "2429 WALBORN DR, Columbus, OH, 43026",
        "result": """The property at 2429 Walborn Dr... is a single-family home...
        Source: zillow.com"""
    },
    {
        "address": "2430 BAYSIDE DR, Columbus, OH, 43026",
        "result": """The property at 2430 Bayside Dr... is likely an apartment...
        Source: search_inference"""
    },
    {
        "address": "2430 CRYSTAL SPRINGS DR, Columbus, OH, 43026",
        "result": """The property at 2430 Crystal Springs Dr... is a condominium...
        Source: zillow.com"""
    },
    {
        "address": "2430 HILLIARD PARK BLVD, Columbus, OH, 43026",
        "result": """The property at 2430 Hilliard Park Blvd... is part of the Hilliard Park Apartments/Townhomes...
        Source: hotpads.com"""
    },
    {
        "address": "2430 MILLS FALL DR, Columbus, OH, 43026",
        "result": """The property at 2430 Mills Fall Dr... is a single-family home...
        Source: zillow.com"""
    },
    {
        "address": "2430 QUARRY STONE DR, Columbus, OH, 43026",
        "result": """The property at 2430 Quarry Stone Dr... is a condo...
        Source: zillow.com"""
    },
    {
        "address": "2430 SPRING ROW LN, Columbus, OH, 43026",
        "result": """The property at 2430 Spring Row Ln... is a condo...
        Source: zillow.com"""
    },
    {
        "address": "2430 SUMMERGREEN DR, Columbus, OH, 43026",
        "result": """The property at 2430 Summergreen Dr... is a condo...
        Source: zillow.com"""
    },
    {
        "address": "2431 BAYSIDE DR, Columbus, OH, 43026",
        "result": """The property at 2431 Bayside Dr... is likely an apartment...
        Source: search_inference"""
    },
    {
        "address": "2431 HILLIARD PARK BLVD, Columbus, OH, 43026",
        "result": """The property at 2431 Hilliard Park Blvd... is part of the Hilliard Park Apartments...
        Source: irtliving.com"""
    },
    {
        "address": "2431 LAKEBRIDGE LN, Columbus, OH, 43026",
        "result": """The property at 2431 Lakebridge Ln... is a condo...
        Source: realtor.com"""
    },
    {
        "address": "2431 PUNDERSON DR, Columbus, OH, 43026",
        "result": """The property at 2431 Punderson Dr... is a single-family freestanding home...
        Source: redfin.com"""
    },
    {
        "address": "2431 SPRING ROW LN, Columbus, OH, 43026",
        "result": """The property at 2431 Spring Row Ln... is a condo...
        Source: zillow.com"""
    },
    {
        "address": "2432 BAYSIDE DR, Columbus, OH, 43026",
        "result": """The property at 2432 Bayside Dr... is likely an apartment...
        Source: search_inference"""
    },
    {
        "address": "2432 CRYSTAL SPRINGS DR, Columbus, OH, 43026",
        "result": """The property at 2432 Crystal Springs Dr... is a condominium...
        Source: zillow.com"""
    },
    {
        "address": "2432 HILLIARD PARK BLVD, Columbus, OH, 43026",
        "result": """The property at 2432 Hilliard Park Blvd... is part of the Hilliard Park Apartments...
        Source: irtliving.com"""
    },
    {
        "address": "2432 PEARSON WAY, Columbus, OH, 43026",
        "result": """The property at 2432 Pearson Way... is a single-family home...
        Source: zillow.com"""
    },
    {
        "address": "2432 QUARRY STONE DR, Columbus, OH, 43026",
        "result": """The property at 2432 Quarry Stone Dr... is a condo...
        Source: zillow.com"""
    },
    {
        "address": "2432 SPRING ROW LN, Columbus, OH, 43026",
        "result": """The property at 2432 Spring Row Ln... is a condo...
        Source: zillow.com"""
    },
    {
        "address": "2432 YAGGER BAY DR, Columbus, OH, 43026",
        "result": """The property at 2432 Yagger Bay Dr... is a single-family home...
        Source: zillow.com"""
    },
    {
        "address": "2433 BAYSIDE DR, Columbus, OH, 43026",
        "result": """The property at 2433 Bayside Dr... is likely an apartment...
        Source: search_inference"""
    },
    {
        "address": "2433 HILLIARD PARK BLVD, Columbus, OH, 43026",
        "result": """The property at 2433 Hilliard Park Blvd... is part of the Hilliard Park Apartments...
        Source: irtliving.com"""
    },
    {
        "address": "2433 LAKEBRIDGE LN, Columbus, OH, 43026",
        "result": """The property at 2433 Lakebridge Ln... is a condo...
        Source: realtor.com"""
    },
    {
        "address": "2433 SPRING ROW LN, Columbus, OH, 43026",
        "result": """The property at 2433 Spring Row Ln... is a condo...
        Source: zillow.com"""
    },
    {
        "address": "2433 SUMMERGREEN DR, Columbus, OH, 43026",
        "result": """The property at 2433 Summergreen Dr... is a condo...
        Source: zillow.com"""
    },
    {
        "address": "2433 WARM SPRINGS DR, Columbus, OH, 43026",
        "result": """The property at 2433 Warm Springs Dr... is a condominium...
        Source: zillow.com"""
    },
    {
        "address": "2433 YAGGER BAY DR, Columbus, OH, 43026",
        "result": """The property at 2433 Yagger Bay Dr... is a single-family home...
        Source: zillow.com"""
    },
    {
        "address": "2434 BAYSIDE DR, Columbus, OH, 43026",
        "result": """The property at 2434 Bayside Dr... is likely an apartment...
        Source: search_inference"""
    },
    {
        "address": "2434 CRYSTAL SPRINGS DR, Columbus, OH, 43026",
        "result": """The property at 2434 Crystal Springs Dr... is a condominium...
        Source: zillow.com"""
    },
    {
        "address": "2434 OAKTHORPE DR, Columbus, OH, 43026",
        "result": """The property at 2434 Oakthorpe Dr... is a single-family home...
        Source: zillow.com"""
    },
    {
        "address": "2434 QUARRY STONE DR, Columbus, OH, 43026",
        "result": """The property at 2434 Quarry Stone Dr... is a condo...
        Source: zillow.com"""
    },
    {
        "address": "2434 SPRING ROW LN, Columbus, OH, 43026",
        "result": """The property at 2434 Spring Row Ln... is a condo...
        Source: zillow.com"""
    },
    {
        "address": "2434 SUMMERGREEN DR, Columbus, OH, 43026",
        "result": """The property at 2434 Summergreen Dr... is a condo...
        Source: zillow.com"""
    },
    {
        "address": "2435 BAYSIDE DR, Columbus, OH, 43026",
        "result": """The property at 2435 Bayside Dr... is likely an apartment...
        Source: search_inference"""
    },
    {
        "address": "2435 HILLIARD PARK BLVD, Columbus, OH, 43026",
        "result": """The property at 2435 Hilliard Park Blvd... is part of the Hilliard Park Apartments...
        Source: irtliving.com"""
    },
    {
        "address": "2435 LAKEBRIDGE LN, Columbus, OH, 43026",
        "result": """The property at 2435 Lakebridge Ln... is a condo...
        Source: realtor.com"""
    },
    {
        "address": "2435 OAKTHORPE DR, Columbus, OH, 43026",
        "result": """The property at 2435 Oakthorpe Dr... is a single-family home...
        Source: zillow.com"""
    },
    {
        "address": "2435 SPRING ROW LN, Columbus, OH, 43026",
        "result": """The property at 2435 Spring Row Ln... is a condo...
        Source: zillow.com"""
    },
    {
        "address": "2435 SUMMERGREEN DR, Columbus, OH, 43026",
        "result": """The property at 2435 Summergreen Dr... is a condo...
        Source: zillow.com"""
    },
    {
        "address": "2435 WARM SPRINGS DR, Columbus, OH, 43026",
        "result": """The property at 2435 Warm Springs Dr... is a condominium...
        Source: zillow.com"""
    },
    {
        "address": "2436 BAYSIDE DR, Columbus, OH, 43026",
        "result": """The property at 2436 Bayside Dr... is likely an apartment...
        Source: search_inference"""
    },
    {
        "address": "2436 HIGHLANDTOWN DR, Columbus, OH, 43026",
        "result": """The property at 2436 Highlandtown Dr... is a single-family home...
        Source: zillow.com"""
    },
    {
        "address": "2436 QUARRY STONE DR, Columbus, OH, 43026",
        "result": """The property at 2436 Quarry Stone Dr... is a condo...
        Source: zillow.com"""
    },
    {
        "address": "2436 SPRING ROW LN, Columbus, OH, 43026",
        "result": """The property at 2436 Spring Row Ln... is a condo...
        Source: zillow.com"""
    },
    {
        "address": "2436 STEWART HOLLOW CT, Columbus, OH, 43026",
        "result": """The property at 2436 Stewart Hollow Ct... is a single-family home...
        Source: zillow.com"""
    },
    {
        "address": "2436 SUMMERGREEN DR, Columbus, OH, 43026",
        "result": """The property at 2436 Summergreen Dr... is a condo...
        Source: realtor.com"""
    },
    {
        "address": "2436 WARM SPRINGS DR, Columbus, OH, 43026",
        "result": """The property at 2436 Warm Springs Dr... is a condominium...
        Source: zillow.com"""
    },
    {
        "address": "2437 BAYSIDE DR, Columbus, OH, 43026",
        "result": """The property at 2437 Bayside Dr... is likely an apartment...
        Source: search_inference"""
    }
]

print("Processing agent batch...")

def classify_address(address, result):
    category = "UNKNOWN"
    property_type = "UNKNOWN"
    result_lower = result.lower()
    
    if "condo" in result_lower or "apartment" in result_lower or "townhome" in result_lower or "condominium" in result_lower or "multi-family" in result_lower or "multifamily" in result_lower or "multi 5+" in result_lower:
        property_type = "CONDO" # or APARTMENT
        if "apartment" in result_lower or "multi 5+" in result_lower: property_type = "APARTMENT"
        category = "RESIDENTIAL"
    elif "single family" in result_lower or "single-family" in result_lower or "house" in result_lower or "freestanding" in result_lower or "patio home" in result_lower:
        property_type = "SINGLE FAMILY"
        category = "RESIDENTIAL"
    elif "commercial" in result_lower or "business" in result_lower or "retail" in result_lower or "office" in result_lower or "plaza" in result_lower or "store" in result_lower or "industrial" in result_lower or "warehouse" in result_lower or "trucking" in result_lower:
        if "auditor's office" in result_lower or "auditor office" in result_lower:
             pass # Skip commercial classification if it's just mentioning the auditor's office
        else:
            category = "COMMERCIAL"
    elif "land" in result_lower or "lot" in result_lower or "vacant" in result_lower or "vacant land" in result_lower:
        category = "LAND"
    elif "residential" in result_lower: 
        category = "RESIDENTIAL"
    
    return category

output_file = "../output/validation_results_43026.csv"

try:
    with open(output_file, 'a', newline='') as f:
        writer = csv.writer(f)
        for item in batch_data:
            classification = classify_address(item['address'], item['result'])
            p_type = "UNKNOWN"
            res_lower = item['result'].lower()
            if "condo" in res_lower or "condominium" in res_lower: p_type = "CONDO"
            elif "single family" in res_lower or "single-family" in res_lower: p_type = "SINGLE FAMILY"
            elif "apartment" in res_lower or "multi-family" in res_lower or "multi 5+" in res_lower: p_type = "APARTMENT"
            
            source = "Agent Search"
            if "zillow" in res_lower: source = "zillow"
            elif "redfin" in res_lower: source = "redfin"
            elif "realtor" in res_lower: source = "realtor"
            elif "movoto" in res_lower: source = "movoto"
            elif "coldwell" in res_lower: source = "coldwellbanker"
            elif "castoinfo" in res_lower: source = "castoinfo.com"
            elif "explorecentralohio" in res_lower: source = "explorecentralohio.com"
            elif "sellingcentralohiohomes" in res_lower: source = "sellingcentralohiohomes.com"
            elif "huff" in res_lower: source = "huff.com"
            elif "ferrari" in res_lower: source = "ferrarihomegroup.com"
            elif "sellingcolumbus" in res_lower: source = "sellingcolumbusoh.com"
            elif "neff" in res_lower: source = "neffgulaucorealestate.com"
            elif "crtrealtors" in res_lower: source = "crtrealtors.com"
            elif "luxeomni" in res_lower: source = "luxeomni.com"
            elif "livewellhomegrp" in res_lower: source = "livewellhomegrp.com"
            elif "paulritterhomes" in res_lower: source = "paulritterhomes.com"
            elif "attomdata" in res_lower: source = "attomdata.com"
            elif "apartments" in res_lower: source = "apartments.com"
            elif "stessa" in res_lower: source = "stessa.com"
            elif "realtyohio" in res_lower: source = "realtyohio.com"
            elif "livewell" in res_lower: source = "livewellhomegrp.com"
            elif "ziffy" in res_lower: source = "ziffy.ai"
            elif "forsalebyowner" in res_lower: source = "forsalebyowner.com"
            elif "capitolohioteam" in res_lower: source = "capitolohioteam.com"
            elif "trulia" in res_lower: source = "trulia.com"
            elif "pamsold" in res_lower: source = "pamsold.com"
            elif "ohiohauntedhouses" in res_lower: source = "ohiohauntedhouses.com"
            elif "cedarone" in res_lower: source = "cedaronerealty.com"
            elif "haring" in res_lower: source = "haringrealty.com"
            elif "mazeandcompany" in res_lower: source = "mazeandcompany.com"
            elif "thecolumbusteam" in res_lower: source = "thecolumbusteam.com"
            elif "ourohiohome" in res_lower: source = "ourohiohome.com"
            elif "deliciousrealestate" in res_lower: source = "deliciousrealestate.com"
            elif "chudikgroup" in res_lower: source = "chudikgroup.com"
            elif "usa1realestate" in res_lower: source = "usa1realestate.com"
            elif "cutlerhomes" in res_lower: source = "cutlerhomes.com"
            elif "loopnet" in res_lower: source = "loopnet.com"
            elif "xome" in res_lower: source = "xome.com"
            elif "realestate2" in res_lower: source = "realestate2.com"
            elif "kwcore" in res_lower: source = "kwcore.com"
            elif "livabl" in res_lower: source = "livabl.com"
            elif "newhomesource" in res_lower: source = "newhomesource.com"
            elif "pulte" in res_lower: source = "pulte.com"
            elif "franklincountyauditor" in res_lower: source = "franklincountyauditor.com"
            elif "bhhsfloridarealty" in res_lower: source = "bhhsfloridarealty.com"
            elif "mdclimited" in res_lower: source = "mdclimited.com"
            elif "dominicfonte" in res_lower: source = "dominicfonte.com"
            elif "estately" in res_lower: source = "estately.com"
            elif "forrent" in res_lower: source = "forrent.com"
            elif "walkertiu" in res_lower: source = "walkertiu.com"
            elif "glasshouserealty" in res_lower: source = "glasshouserealty.com"
            elif "oldhouses" in res_lower: source = "oldhouses.com"
            elif "homegeniusrealestate" in res_lower: source = "homegeniusrealestate.com"
            elif "homes" in res_lower: source = "homes.com"
            elif "robyrealty" in res_lower: source = "robyrealty.com"
            elif "richrussorealty" in res_lower: source = "richrussorealty.com"
            elif "allaboutcentralohio" in res_lower: source = "allaboutcentralohio.com"
            elif "redfrogrealty" in res_lower: source = "redfrogrealty.com"
            elif "realistar" in res_lower: source = "realistar.com"
            elif "parcels" in res_lower: source = "parcels.contact"
            elif "propertyfocus" in res_lower: source = "propertyfocus.com"
            elif "rentprogress" in res_lower: source = "rentprogress.com"
            elif "rollsrealty" in res_lower: source = "rollsrealty.com"
            elif "buckeyerealtygroup" in res_lower: source = "buckeyerealtygroup.com"
            elif "shannonlistshomes" in res_lower: source = "shannonlistshomes.com"
            elif "galleryhomesrealestate" in res_lower: source = "galleryhomesrealestate.com"
            elif "ikeyrealty" in res_lower: source = "ikeyrealty.com"
            elif "sarahbmoorehomes" in res_lower: source = "sarahbmoorehomes.com"
            elif "galbreathrealestate" in res_lower: source = "galbreathrealestate.com"
            elif "sethjanitzki" in res_lower: source = "sethjanitzki.com"
            elif "championohioteam" in res_lower: source = "championohioteam.com"
            elif "centralohiohomeguide" in res_lower: source = "centralohiohomeguide.com"
            elif "apartmentfinder" in res_lower: source = "apartmentfinder.com"
            elif "hotpads" in res_lower: source = "hotpads.com"
            elif "ryanreynoldsteam" in res_lower: source = "ryanreynoldsteam.com"
            elif "columbushomeownership" in res_lower: source = "columbushomeownership.com"
            elif "affordablehousingonline" in res_lower: source = "affordablehousingonline.com"
            elif "apartmenthomeliving" in res_lower: source = "apartmenthomeliving.com"
            elif "forrentuniversity" in res_lower: source = "forrentuniversity.com"
            elif "susannecasey" in res_lower: source = "susannecasey.com"
            elif "visionrealty" in res_lower: source = "visionrealty.com"
            elif "themikelaemmleteamrealty" in res_lower: source = "themikelaemmleteamrealty.com"
            elif "carolgoffrealestate" in res_lower: source = "carolgoffrealestate.com"
            elif "morgan-properties" in res_lower: source = "morgan-properties.com"
            elif "columbus.gov" in res_lower: source = "columbus.gov"
            elif "apartmentguide" in res_lower: source = "apartmentguide.com"
            elif "corporatehousing" in res_lower: source = "corporatehousing.com"
            elif "remax" in res_lower: source = "remax.com"
            elif "franklincountyauditors" in res_lower: source = "franklincountyauditors.org"
            elif "franklincountytax" in res_lower: source = "franklincountytax.us"
            elif "ohiovalleyrealestateguide" in res_lower: source = "ohiovalleyrealestateguide.com"
            elif "lesleeloveshomes" in res_lower: source = "lesleeloveshomes.com"
            elif "bluegrasspropertiesgroup" in res_lower: source = "bluegrasspropertiesgroup"
            elif "joehaydenrealtor" in res_lower: source = "joehaydenrealtor"
            elif "homesbuykristen" in res_lower: source = "homesbuykristen.com"
            elif "howardhanna" in res_lower: source = "howardhanna.com"
            elif "waynelwoods" in res_lower: source = "waynelwoods.com"
            elif "mapszipcode" in res_lower: source = "mapszipcode.com"
            elif "zipdatamaps" in res_lower: source = "zipdatamaps.com"
            elif "zipcodestogo" in res_lower: source = "zipcodestogo.com"
            elif "unitedstateszipcodes" in res_lower: source = "unitedstateszipcodes.org"
            elif "postcodebase" in res_lower: source = "postcodebase.com"
            elif "homegenius" in res_lower: source = "homegeniusrealestate.com"
            elif "pattisonrealestate" in res_lower: source = "pattisonrealestate.com"
            elif "har" in res_lower: source = "har.com"
            elif "zipcode" in res_lower: source = "zipcode.org"
            elif "e-merge" in res_lower: source = "e-merge.com"
            elif "livegableswest" in res_lower: source = "livegableswest.com"
            elif "rentcafe" in res_lower: source = "rentcafe.com"
            elif "propertychecker" in res_lower: source = "propertychecker.com"
            elif "sfranalytics" in res_lower: source = "sfranalytics.com"
            elif "franklincountyohio" in res_lower: source = "franklincountyohio.gov"
            elif "crexi" in res_lower: source = "crexi.com"
            elif "localrealestateonline" in res_lower: source = "localrealestateonline.com"
            elif "propertypanorama" in res_lower: source = "propertypanorama.com"
            elif "hudwayglass" in res_lower: source = "hudwayglass.com"
            elif "cityfeet" in res_lower: source = "cityfeet.com"
            elif "showcase" in res_lower: source = "showcase.com"
            elif "moovitapp" in res_lower: source = "moovitapp.com"
            elif "arcgis" in res_lower: source = "arcgis.com"
            elif "liveoakwood" in res_lower: source = "liveoakwood.com"
            elif "assistedlivingcenter" in res_lower: source = "assistedlivingcenter.com"
            elif "apartmentlist" in res_lower: source = "apartmentlist.com"
            elif "yardimatrix" in res_lower: source = "yardimatrix.com"
            elif "rentseeker" in res_lower: source = "rentseeker.com"
            elif "thewintergroup614" in res_lower: source = "thewintergroup614.com"
            elif "propertyreach" in res_lower: source = "propertyreach.com"
            elif "bayside-trprop" in res_lower: source = "bayside-trprop.com"
            elif "collinslassitergroup" in res_lower: source = "collinslassitergroup.com"
            elif "countryviewwest-trprop" in res_lower: source = "countryviewwest-trprop.com"
            elif "zumper" in res_lower: source = "zumper.com"
            elif "hilliardohio" in res_lower: source = "hilliardohio.gov"
            elif "attomdata" in res_lower: source = "attomdata.com"
            elif "carolgoffrealestate" in res_lower: source = "carolgoffrealestate.com"
            elif "heppner-homes" in res_lower: source = "heppner-homes.com"
            elif "meachamrealestate" in res_lower: source = "meachamrealestate.com"
            elif "capraterealty" in res_lower: source = "capraterealty.com"
            elif "zoocasa" in res_lower: source = "zoocasa.com"
            elif "irtliving" in res_lower: source = "irtliving.com"
            elif "rentable" in res_lower: source = "rentable.co"
            elif "point2homes" in res_lower: source = "point2homes.com"
            elif "douglasandassociatesrealty" in res_lower: source = "douglasandassociatesrealty.com"

            writer.writerow([item['address'], classification, p_type, source])
            print(f"Saved: {item['address']} -> {classification}")

    print("Batch processing complete.")

except Exception as e:
    print(f"Error saving batch: {e}")
