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
                 element_key=None, where=None, source=None, store=None):
        Enricher.__init__(self, name)
        self.elementwise = fn_elementwise if fn_elementwise else lambda x: x
        self.aggregate   = fn_aggregate
        self.collection  = dict([])
        self.key    = element_key
        self.where  = self.enforce_key(where)
        self.source = self.enforce_key(source)
        self.store  = self.enforce_key(store)
    
    def enforce_key(self, key):
        if not key:
            return None
        # all ints are allowed
        if type(key) == int:
            return key
        # strings must not be empty
        if type(key) == str:
            return key if len(key) > 0 else None
        # no other type support
        return None

    def flush(self):
        # reset for new collection of comments
        self.collection = dict([])

    def collect(self, element, store=None, fn=None):
        # must have a destination bucket
        if not store:
            store = self.store if self.store is not None else None
        if store is None:
            return False
        if store not in self.collection.keys():
            self.collection[store] = list()
        # collect
        self.collection[store].append(
            # apply elementwise function, if specified
            self.elementwise(element if self.key is None else element[self.key]) \
                if callable(self.elementwise) \
                else lambda x: x # default fn (does nothing)
        )
        # success
        return True
    
    def dump(self, source=None, where=None, fn=None):
        func = fn if fn is not None else self.aggregate
        source = source if source is not None else self.source
        where  = where  if where  is not None else self.where
        # aggregate/source not defined, do nothing and dump raw to where
        if not callable(func) or source is None:
            self.collection[where] = self.collection[source]
            return None
        # no destination defined, return aggregated value
        if not where:
            return func(self.collection[source])
        # otherwise, dump at destination
        self.collection[where] = func(self.collection[source])
        return None

class EnrichmentPipeline():
    def __init__(self, comment_enrichers=[]):
        for ce in comment_enrichers:
            assert type(ce) == Aggregator
        self.comment_enrichers = comment_enrichers
    
    def collect_all(self, comment, stores=None, fns=None):
        # TODO: zipped multiple different parameters (as lists)
        for ce in self.comment_enrichers:
            ce.collect(comment, None, None)
    
    def dump_all(self, sources=None, wheres=None, fns=None):
        # TODO: zipped multiple different parameters (as lists)
        for ce in self.comment_enrichers:
            ce.dump(None, None, None)

ZSCORE_AGGREGATOR = Aggregator(name='zscore',
                               fn_elementwise=None,
                               fn_aggregate=stats.zscore,
                               element_key='score',
                               store='zscore_collection',
                               source='zscore_collection',
                               where=1)

# more complex since an external model is required
def get_entities(element):
    spacy_nlp = spacy.load('en')
    entities = spacy_nlp(element).ents
    return [{item.label_: item.text} for item in entities]

ENTITIES_AGGREGATOR = Aggregator(name='entities',
                                 fn_elementwise=get_entities,
                                 fn_aggregate=None,
                                 element_key='body',
                                 store='entity_collection',
                                 source='entity_collection',
                                 where='entity_collection')

# more complex since an external model is required
def afinn_elementwise(element):
    afinn_nlp = afinn.Afinn(language='en', emoticons=True)
    return afinn_nlp.score(element)

AFINN_AGGREGATOR = Aggregator(name='afinn_score',
                              fn_elementwise=afinn_elementwise,
                              fn_aggregate=None,
                              element_key='body',
                              store='afinn_collection',
                              source='afinn_collection',
                              where='afinn_collection')

def load_as_dict(path):
    try:
        with open(path) as f:
            return json.load(f)
    except Exception as e:
        print(e)
        return None

def validate(data):
    # verify type
    assert data and type(data) == list, 'unexpected input type: {0}'.format(type(data))
    # verify structure integrity
    assert data[0]['comments']
    assert data[0]['id']
    assert type(data[0]['score']) == int
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
            ce.dump()
        i = 0
        for comment in submission['comments']:
            for ce in comment_enrichers:
                comment[ce.name] = ce.collection[ce.where][i]
            i += 1
        # flush all
        for ce in comment_enrichers:
            ce.flush()

    return data

def enrich_test(path):
    return enrich(path, [ZSCORE_AGGREGATOR, ENTITIES_AGGREGATOR, AFINN_AGGREGATOR])