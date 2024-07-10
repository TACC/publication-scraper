#!/usr/bin/env python3
import argparse
import json
import requests
import xmltodict

ESEARCH_URL='https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi'
# https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pmc&term=Joshua+Lederberg%5Bauthor%5D
ESUMMARY_URL='https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi'
# https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pmc&id=7840891&retmode=json

parser = argparse.ArgumentParser()
parser.add_argument('-n', '--name', type=str, required=True, help='Author name, e.g. First M Last')
args = parser.parse_args()


def main():
    search_name = args.name.replace(' ', '+')
    r = requests.get(f'{ESEARCH_URL}?db=pmc&term={search_name}%5Bauthor%5D')
    data = xmltodict.parse(r.text)
    id_list = data['eSearchResult']['IdList']['Id']

    for item in id_list[:1]:
        r = requests.get(f'{ESUMMARY_URL}?db=pmc&id={item}&retmode=json')
        print(json.dumps(r.json(), indent=2))

if __name__ == '__main__':
    main()
