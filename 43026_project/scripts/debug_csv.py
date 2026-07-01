
import csv
import os

OUTPUT_FILE = '../output/validation_results_43026.csv'

def check_csv():
    if not os.path.isfile(OUTPUT_FILE):
        print("File not found")
        return

    print(f"File size: {os.path.getsize(OUTPUT_FILE)} bytes")
    
    with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        print(f"Total lines: {len(lines)}")
        print("Last 5 lines:")
        for l in lines[-5:]:
            print(repr(l))

    processed = set()
    try:
        with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            print(f"Header: {reader.fieldnames}")
            count = 0
            for row in reader:
                count += 1
                if 'address' in row:
                    processed.add(row['address'])
            print(f"Total rows parsed: {count}")
            print(f"Unique addresses: {len(processed)}")
    except Exception as e:
        print(f"Error parsing DictReader: {e}")

if __name__ == "__main__":
    check_csv()
