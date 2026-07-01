import csv
import os

input_file = '../data/addresses_43213_formatted.csv'
output_dir = '../split_addresses_43213'
chunk_size = 1000

os.makedirs(output_dir, exist_ok=True)

with open(input_file, 'r') as f:
    reader = csv.reader(f)
    header = next(reader)

    chunk = []
    file_count = 1

    for row in reader:
        chunk.append(row)
        if len(chunk) == chunk_size:
            output_file = os.path.join(output_dir, f'addresses_43213_part_{file_count:02d}.csv')
            with open(output_file, 'w', newline='') as out_f:
                writer = csv.writer(out_f)
                writer.writerow(header)
                writer.writerows(chunk)
            print(f"Created {output_file} with {len(chunk)} records")
            chunk = []
            file_count += 1

    # Write remaining records
    if chunk:
        output_file = os.path.join(output_dir, f'addresses_43213_part_{file_count:02d}.csv')
        with open(output_file, 'w', newline='') as out_f:
            writer = csv.writer(out_f)
            writer.writerow(header)
            writer.writerows(chunk)
        print(f"Created {output_file} with {len(chunk)} records")

print("Splitting complete.")
