import re

input_file = 'risk_review_list.txt'
units_file = 'risk_units.txt'
non_units_file = 'risk_non_units.txt'

with open(input_file, 'r') as f_in, open(units_file, 'w') as f_units, open(non_units_file, 'w') as f_non:
    for line in f_in:
        line = line.strip()
        upper = line.upper()
        
        # Check for unit indicators
        # " APT ", " UNIT ", " #", " BLDG ", " STE ", " SUITE " (already removed suites)
        # Also patterns like "D31", "B15" at the end often indicate units.
        
        is_unit = False
        if " APT " in upper or " UNIT " in upper or " # " in upper or " BLDG " in upper:
            is_unit = True
        elif re.search(r'\s[A-Z]\d+$', upper): # Matches " D31"
            is_unit = True
        elif re.search(r'\s\d+[A-Z]$', upper): # Matches " 2B"
            is_unit = True
        elif re.search(r'\s[A-Z]$', upper): # Matches " A" (e.g. 123 Main St A)
            is_unit = True
            
        if is_unit:
            f_units.write(line + '\n')
        else:
            f_non.write(line + '\n')

print("Separation complete.")
