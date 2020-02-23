'''
enrichment.py
    targets collected data (./data/*.json), provides enrichment options...
    also contains tools for parsing collected data
'''

import os
import json
import afinn
import spacy
import scipy.stats as stats

class Enricher:
    def __init__(self, name):
        self.name = name

class Aggregator(Enricher):
    def __init__(self, name, fn_elementwise=None, fn_aggregate=None, \
                 where=None, source=None):
        Enricher.__init__(self, name)
        self.elementwise = fn_elementwise if fn_elementwise else lambda x: x
        self.aggregate   = fn_aggregate
        self.collection  = dict([])
        self.where  = where  if where  and len(where)  > 0 else None
        self.source = source if source and len(source) > 0 else None
    
    def collect(self, element, where, fn=None):
        # must have a destination bucket
        if not where or len(where) == 0 or not self.where:
            return False
        if where not in self.collection.keys():
            self.collection[where] = list()
        # collect
        self.collection[where].append(
            # apply elementwise function, if specified
            self.elementwise(element) \
                if self.elementwise \
                else lambda x: x # default fn (does nothing)
        )
        # success
        return True
    
    def dump(self, source=None, where=None, fn=None):
        func = fn if fn else self.aggregate
        source = source if source and len(source) > 0 else self.source
        where  = where  if where  and len(where)  > 0 else self.where
        # aggregate/source not defined, do nothing
        if func is None or source is None:
            return None
        # no destination defined, return aggregated value
        if not where:
            return func(self.collection[source])
        # otherwise, dump at destination
        self.collection[where] = func(self.collection[source])
        return None

ZSCORE_AGGREGATOR = Aggregator(name='zscore',
                               fn_elementwise=None,
                               fn_aggregate=stats.zscore,
                               where='zscore_collection')

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

def enrich(path, comment_enrichers=[], submission_enrichers=[]):
    data = load_as_dict(path)
    # validation step, begin work after
    validate(data)
    # TODO: deal w submission enrichers later...
    # enrich data
    for submission in data:
        # collect all comments
        for comment in submission['comments']:    
            # add to all enrichers
            for ce in comment_enrichers:
                ce.collect(comment)
        # aggregate all
        for ce in comment_enrichers:
            # assume: no where provided for Aggregators
            data[ce.name] = ce.dump()

    return data

def enrich_test(path):
    return enrich(path, [ZSCORE_AGGREGATOR])