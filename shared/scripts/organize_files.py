#!/usr/bin/env python3
"""
Organize Address project files into folders by zip code.
"""
import os
import shutil
import glob

base = '/Users/kevinpatel/Address'

# Create folder structure
for zipcode in ['43026', '43123', '43204', '43223', '43229']:
    for sub in ['data', 'scripts', 'output']:
        os.makedirs(f'{base}/{zipcode}_project/{sub}', exist_ok=True)

os.makedirs(f'{base}/shared_scripts', exist_ok=True)
os.makedirs(f'{base}/master_data', exist_ok=True)

# Move files by pattern
moves = [
    # 43026
    ('addresses_43026*.csv', '43026_project/data/'),
    ('validation_results_43026*', '43026_project/output/'),
    ('validation_43026*.log', '43026_project/output/'),
    ('validate_43026*.py', '43026_project/scripts/'),
    
    # 43123
    ('addresses_43123*.csv', '43123_project/data/'),
    ('*43123*.py', '43123_project/scripts/'),
    
    # 43204
    ('addresses_43204*', '43204_project/data/'),
    
    # 43223
    ('addresses_43223*.csv', '43223_project/data/'),
    ('*43223*.txt', '43223_project/output/'),
    ('*43223*.py', '43223_project/scripts/'),
    
    # 43229
    ('addresses_43229*.csv', '43229_project/data/'),
    ('validation_results_43229*', '43229_project/output/'),
    ('validation_43229*.log', '43229_project/output/'),
    ('validate_43229*.py', '43229_project/scripts/'),
    
    # Master data
    ('addresses.txt', 'master_data/'),
    ('addresses_clean.csv', 'master_data/'),
    ('addresses_with_coords.txt', 'master_data/'),
    ('addresses_all_zips*', 'master_data/'),
]

moved = 0
for pattern, dest in moves:
    for f in glob.glob(f'{base}/{pattern}'):
        if os.path.exists(f) and os.path.isfile(f):
            try:
                fname = os.path.basename(f)
                shutil.move(f, f'{base}/{dest}{fname}')
                moved += 1
                print(f'Moved: {fname} -> {dest}')
            except Exception as e:
                print(f'Error: {f}: {e}')

print(f'\nTotal: Moved {moved} files')
