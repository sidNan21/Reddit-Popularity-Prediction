'''
enrich.py
    targets collected data (./data/*.json), provides enrichment options...
    also contains tools for parsing collected data
'''

import os
import json
import afinn
import spacy

from scipy.stats import zscore

def load_as_dict(dir):
    try:
        with open(dir) as f:
            return json.load(f)
    except Exception as e:
        print(e)
        return None

def zscore_enricher(comment):
    return None

def afinn_enricher(comment):
    return None

def spacy_enricher(comment):
    return None

def enrich(enrichers=[]):
    return None
