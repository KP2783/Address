import csv
import shutil
import os

input_file = 'addresses_43026_residential_final.csv'
temp_file = 'addresses_43026_residential_final_temp.csv'

with open(input_file, 'r') as f_in, open(temp_file, 'w', newline='') as f_out:
    reader = csv.DictReader(f_in)
    # We only want the 'address' column
    fieldnames = ['address']
    writer = csv.DictWriter(f_out, fieldnames=fieldnames)
    writer.writeheader()
    
    for row in reader:
        writer.writerow({'address': row['address']})

# Replace the original file
os.replace(temp_file, input_file)
print(f"Updated {input_file} to contain only the 'address' column.")
