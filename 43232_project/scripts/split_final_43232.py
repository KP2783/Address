#!/usr/bin/env python3
"""Split the validated 43232 residential list into single-column CSV shards.

Format (per your choice): single 'address' column, Title-case address line.
Each shard holds up to 1000 rows. Naming: addresses_43232_part_NN.csv.
Source: addresses_43232_residential_final.csv (11,782 validated residential).
"""
import csv
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ZIP = '43232'
SRC = os.path.join(SCRIPT_DIR, '..', 'data', f'addresses_{ZIP}_residential_final.csv')
OUTDIR = os.path.join(SCRIPT_DIR, '..', f'split_addresses_{ZIP}')
CHUNK = 1000


def titlecase(s):
    """Title-case preserving digit-leading tokens (e.g. '23RD', '2S') and hyphens."""
    out = []
    for tok in (s or '').split():
        if tok[:1].isdigit():
            out.append(tok)
        else:
            out.append('-'.join(p.capitalize() if (p and not p[:1].isdigit()) else p
                                for p in tok.split('-')))
    return ' '.join(out)


def main():
    os.makedirs(OUTDIR, exist_ok=True)
    chunk = []
    file_no = 0
    total = 0
    src = csv.DictReader(open(SRC, newline=''))

    def flush():
        nonlocal file_no
        if not chunk:
            return
        file_no += 1
        path = os.path.join(OUTDIR, f'addresses_{ZIP}_part_{file_no:02d}.csv')
        with open(path, 'w', newline='') as f:
            f.write('address\n')          # plain header, no quoting (matches other ZIPs' shards)
            f.writelines(line + '\n' for line in chunk)
        print(f'  {os.path.basename(path)}: {len(chunk)} rows')

    for r in src:
        number = r['number']
        street = titlecase(r['street'])
        unit = (r.get('unit') or '').strip()
        unit_part = f' {titlecase(unit)}' if unit else ''
        city = (r.get('city') or 'Columbus').strip() or 'Columbus'
        city = city.title()  # already Title, ensure
        line = f'{number} {street}{unit_part}, {city}, OH, {ZIP}'
        chunk.append(line)
        total += 1
        if len(chunk) >= CHUNK:
            flush()
            chunk = []
    flush()

    print(f'\nTotal addresses: {total} -> {file_no} file(s) in {OUTDIR}')


if __name__ == '__main__':
    main()
