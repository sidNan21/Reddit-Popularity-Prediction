'''
enrich.py
    enrichment of raw reddit data stored as .json in ./data/
'''

from src import enrichment as enrich
from src import tools as tools
import sys
import json

# hard-coded example
data = enrich.enrich_test('./data/Coronavirus.json')
tools.save_json(data, 'ENRICHED_Coronavirus.json')
