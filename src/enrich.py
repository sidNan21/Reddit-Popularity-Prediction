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

class Enricher:
    def __init__(self, fn, name, ag=False):
        self.enrichfn   = fn
        self.aggregator = ag
        self.enrichname = name
        # simple bucket for flexible addition of fields
        self.bucket = dict([])
    
    def enrich(self, comment):
        # apply function
        return self.enrichfn(comment)

def load_as_dict(path):
    try:
        with open(path) as f:
            return json.load(f)
    except Exception as e:
        print(e)
        return None

def validate(data):
    # verify type
    assert data and type(data) == type(dict)
    # verify structure integrity
    assert data[0]['comments']
    assert data[0]['id']
    assert type(data[0]['score']) == type(int)
    assert len(data[0]['comments']) > 0 

def zscore_enrichment():
    return None

def afinn_enrichment():
    return None

def spacy_enrichment():
    return None

'''
'''
def enrich_comments(path, fn_elementwise=[], fn_aggregator=[]):
    data = load_as_dict(path)
    # validation step, begin work after
    validate(data)
    # allocate data for enrichers
    element_enrichers   = list()
    aggregate_enrichers = list()
    for fn in fn_elementwise:
        # must be a tuple with function info
        assert type(fn) == type(tuple) and callable(fn[1])
        e = Enricher(fn, name=fn[0])
        element_enrichers.append(e)
    # for fn in fn_aggregator:
    #     # must be a tuple with function info
    #     assert type(fn) == type(tuple) and callable(fn[1])
    #     e = Enricher(fn, ag=True, name=fn[0])
    #     e.bucket['scores'] = list()
    # enrich data
    for comment in data['comments']:
        # element-wise enrichment
        for enricher in element_enrichers:
            comment[enricher.name] = enricher.enrich(comment)
        # aggregation enrichment, just append
        # for enricher in aggregate_enrichers:
        #     enricher.bucket['scores'].append(comment)
    # apply aggregate enrichment
    # for enricher in aggregate_enrichers:
    #     comment[enricher.name] = enricher.enrich(enricher.bucket['scores'])
    return data
