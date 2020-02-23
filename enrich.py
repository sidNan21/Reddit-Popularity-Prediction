'''
enrich.py
'''

import src.enrichment as enrich
import src.fetch as fetch
import sys
import json

data = enrich.enrich_test('./data/art_top10week_example.json')
fetch.save_json(data, './data/art_top10week_enriched_example.json')
