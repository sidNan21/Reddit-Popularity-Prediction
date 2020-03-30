'''
enrich.py
    enrichment of raw reddit data stored as .json in ./data/
'''

import src.enrichment as enrich
import src.tools as tools
import sys
import json

# hard-coded example
data = enrich.enrich_test('./data/art_top10week_example.json')
tools.save_json(data, 'REVAMP_art_top10week_enriched_example')
