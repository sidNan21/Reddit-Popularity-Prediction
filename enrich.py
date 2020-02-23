'''
enrich.py
'''

import src.enrichment as enrich
import src.tools as tools
import sys
import json

data = enrich.enrich_test('./data/art_top10week_example.json')
tools.save_json(data, 'art_top10week_enriched_example')
