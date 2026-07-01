#!/usr/bin/env python3
"""
Address validation module using Google search results.
Core classification logic for determining residential vs commercial addresses.
"""
import re
from typing import Dict, List, Tuple

# Commercial indicators by confidence level
COMMERCIAL_INDICATORS = {
    'high_confidence': [
        # Business entity types
        'LLC', 'Inc', 'Corp', 'Corporation', 'Company', 'Ltd', 'Limited',
        'business', 'commercial property', 'retail', 'wholesale',
        # Specific business types
        'restaurant', 'store', 'shop', 'mall', 'plaza', 'shopping center',
        'hotel', 'motel', 'inn', 'lodge',
        'bank', 'credit union', 'financial',
        'gas station', 'fuel', 'convenience store',
        'auto dealer', 'car dealership', 'auto sales',
        'warehouse', 'distribution center', 'industrial',
        'factory', 'manufacturing', 'plant',
    ],
    'medium_confidence': [
        # Could be commercial or residential
        'office', 'suite', 'professional',
        'center', 'complex', 'building',
        'salon', 'spa', 'barber',
        'clinic', 'medical', 'dental', 'doctor',
        'law office', 'attorney', 'lawyer',
        'real estate', 'insurance', 'agency',
    ],
    'institutional': [
        # Non-residential but not commercial
        'church', 'temple', 'mosque', 'synagogue', 'religious',
        'school', 'academy', 'university', 'college', 'education',
        'hospital', 'emergency', 'urgent care',
        'government', 'city hall', 'county', 'municipal',
        'fire station', 'police', 'post office',
        'library', 'museum', 'community center',
        'cemetery', 'funeral home', 'mortuary',
    ],
    'vacant_land': [
        'vacant lot', 'empty lot', 'undeveloped',
        'for sale', 'land for sale', 'buildable lot',
        'no structure', 'cleared land',
    ]
}

# Residential indicators (positive signals)
RESIDENTIAL_INDICATORS = [
    'single family', 'single-family', 'residence', 'residential',
    'home', 'house', 'apartment', 'condo', 'condominium',
    'townhouse', 'townhome', 'duplex', 'triplex',
    'zillow', 'realtor', 'redfin', 'trulia',  # Real estate listing sites
    'beds', 'baths', 'bedroom', 'bathroom', 'sqft', 'sq ft',
    'homeowner', 'property owner',
]

def build_search_query(address: str) -> str:
    """
    Build an optimized search query for the address.
    
    Args:
        address: Full formatted address
        
    Returns:
        Search query string
    """
    # Clean up the address
    clean_addr = address.strip()
    # Simple query - just the address
    return f'"{clean_addr}"'


def parse_search_result(result: str, address: str) -> Dict:
    """
    Parse search result text and extract indicators.
    """
    result_lower = result.lower()
    
    indicators = {
        'high_confidence_commercial': [],
        'medium_confidence_commercial': [],
        'institutional': [],
        'vacant_land': [],
        'residential': [],
    }
    
    # Check for commercial indicators
    for indicator in COMMERCIAL_INDICATORS['high_confidence']:
        if indicator.lower() in result_lower:
            indicators['high_confidence_commercial'].append(indicator)
    
    for indicator in COMMERCIAL_INDICATORS['medium_confidence']:
        if indicator.lower() in result_lower:
            indicators['medium_confidence_commercial'].append(indicator)
    
    for indicator in COMMERCIAL_INDICATORS['institutional']:
        if indicator.lower() in result_lower:
            indicators['institutional'].append(indicator)
    
    for indicator in COMMERCIAL_INDICATORS['vacant_land']:
        if indicator.lower() in result_lower:
            indicators['vacant_land'].append(indicator)
    
    # Check for residential indicators
    for indicator in RESIDENTIAL_INDICATORS:
        if indicator.lower() in result_lower:
            indicators['residential'].append(indicator)
    
    return indicators

def extract_property_details(result: str) -> Tuple[str, str]:
    """
    Extract property type and source from search result.
    Returns: (property_type, source)
    """
    result_lower = result.lower()
    
    # Sources
    sources = {
        'Zillow': ['zillow.com', 'zillow'],
        'Redfin': ['redfin.com', 'redfin'],
        'Realtor': ['realtor.com', 'realtor'],
        'Trulia': ['trulia.com', 'trulia'],
        'Apartments.com': ['apartments.com'],
        'LoopNet': ['loopnet.com', 'loopnet'],
        'CoStar': ['costar.com', 'costar'],
        'Homes.com': ['homes.com'],
    }
    
    found_source = 'pending'
    for source_name, keywords in sources.items():
        if any(k in result_lower for k in keywords):
            found_source = source_name
            break
            
    # Property Types
    types = {
        'apartment': ['apartment', 'apts', 'unit', 'multifamily', 'multi-family'],
        'condo': ['condo', 'condominium'],
        'townhome': ['townhome', 'townhouse'],
        'mobile-home': ['mobile home', 'trailer'],
        'vacant-lot': ['vacant lot', 'land', 'undeveloped'],
        'single-family': ['single family', 'single-family', 'house', 'home'],
    }
    
    found_type = 'single-family'  # Default
    for type_name, keywords in types.items():
        if any(k in result_lower for k in keywords):
            found_type = type_name
            break
            
    return found_type, found_source

def classify_address(indicators: Dict) -> Tuple[str, float, str]:
    """
    Classify address based on extracted indicators.
    Returns: (classification, confidence, reason)
    """
    # Count indicators
    high_commercial = len(indicators['high_confidence_commercial'])
    med_commercial = len(indicators['medium_confidence_commercial'])
    institutional = len(indicators['institutional'])
    vacant = len(indicators['vacant_land'])
    residential = len(indicators['residential'])
    
    # Classification Logic
    if high_commercial >= 2:
        return ('COMMERCIAL', 0.95, f"Multiple commercial: {', '.join(indicators['high_confidence_commercial'][:3])}")
    
    if high_commercial == 1 and residential == 0:
        return ('COMMERCIAL', 0.85, f"Commercial found: {indicators['high_confidence_commercial'][0]}")
    
    if institutional >= 1:
        return ('INSTITUTIONAL', 0.90, f"Institutional: {', '.join(indicators['institutional'][:2])}")
    
    if vacant >= 1:
        return ('VACANT', 0.80, f"Vacant land: {', '.join(indicators['vacant_land'][:2])}")
    
    if med_commercial >= 2 and residential == 0:
        return ('COMMERCIAL', 0.65, f"Possible commercial: {', '.join(indicators['medium_confidence_commercial'][:2])}")
    
    if residential >= 1:
        return ('RESIDENTIAL', 0.90, f"Residential indicators: {', '.join(indicators['residential'][:3])}")
        
    return ('RESIDENTIAL', 0.60, "Assumed residential")

def validate_address(address: str, search_result: str) -> Dict:
    """
    Full validation pipeline for a single address.
    """
    if not search_result or len(search_result) < 10:
        return {
            'address': address,
            'classification': 'PENDING',
            'property_type': 'unknown',
            'source': 'pending',
            'confidence': 0.0,
            'reason': 'No search results'
        }

    indicators = parse_search_result(search_result, address)
    classification, confidence, reason = classify_address(indicators)
    property_type, source = extract_property_details(search_result)
    
    # Refine classification based on property type
    if property_type == 'vacant-lot' and classification == 'RESIDENTIAL':
        classification = 'VACANT'
    
    return {
        'address': address,
        'classification': classification,
        'property_type': property_type,
        'source': source,
        'confidence': confidence,
        'reason': reason,
        'indicators': indicators,
    }

