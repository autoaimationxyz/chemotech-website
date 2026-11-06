#!/usr/bin/env python3
"""Import master-list tables while retaining website IDs and reading the latest display numbers."""
import argparse
import json
import re
from pathlib import Path
from zipfile import ZipFile
import xml.etree.ElementTree as ET


def read_master(path, existing):
    ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
    def text(element):
        return ''.join(t.text or '' for t in element.findall('.//w:t', ns))
    with ZipFile(path) as document:
        root = ET.fromstring(document.read('word/document.xml'))
    products, summary, current = [], {}, None
    for element in root.find('w:body', ns):
        if element.tag.endswith('}p'):
            value = text(element)
            heading = re.match(r'^(\d{2})\.\s+(.+)', value)
            if heading:
                current = {'catalogue_no': int(heading[1]), 'name': heading[2], 'desc': '', 'note': '', 'variants': []}
                products.append(current)
            elif current and value:
                if not current['desc']:
                    current['desc'] = value
                else:
                    current['note'] += (' ' if current['note'] else '') + value
        elif element.tag.endswith('}tbl'):
            for row in element.findall('w:tr', ns)[1:]:
                columns = [text(cell) for cell in row.findall('w:tc', ns)]
                if current is None and len(columns) == 4 and columns[0].isdigit():
                    summary[int(columns[0])] = ([m.strip() for m in columns[2].split('·') if m.strip()], int(columns[3]))
                elif current is not None and len(columns) == 2:
                    current['variants'].append({'name': '' if columns[0] == '—' else columns[0], 'makes': [m.strip() for m in columns[1].split(',') if m.strip()]})
    if not products or len(products) != len(summary):
        raise ValueError('Detailed products and summary table do not agree; no output written.')
    stable = {p['name']: p['no'] for p in existing}
    next_id = max(stable.values(), default=0) + 1
    for product in products:
        number = product['catalogue_no']
        makes, expected_variants = summary[number]
        if not product['desc'] or len(product['variants']) != expected_variants:
            raise ValueError(f'Product {number}: missing description or variant count mismatch.')
        product['main_makes'] = makes
        if product['name'] not in stable:
            stable[product['name']] = next_id
            next_id += 1
        product['no'] = stable[product['name']]
    if sorted(p['catalogue_no'] for p in products) != list(range(1, len(products) + 1)):
        raise ValueError('Duplicate or missing source product numbers.')
    if len({p['no'] for p in products}) != len(products):
        raise ValueError('Duplicate stable website IDs.')
    return products


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('document', type=Path)
    parser.add_argument('--output', type=Path, default=Path(__file__).with_name('products.json'))
    parser.add_argument('--check', action='store_true', help='Compare against the current JSON without changing it.')
    args = parser.parse_args()
    existing = json.loads(args.output.read_text(encoding='utf-8')) if args.output.exists() else []
    products = read_master(args.document, existing)
    if args.check:
        if products != existing:
            raise SystemExit('The master list differs from the saved product data.')
        print('Master list matches all saved product descriptions, makes, variants and display numbers.')
    else:
        args.output.write_text(json.dumps(products, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        print(f'Imported {len(products)} product families / {sum(len(p["variants"]) for p in products)} variants.')


if __name__ == '__main__':
    main()
