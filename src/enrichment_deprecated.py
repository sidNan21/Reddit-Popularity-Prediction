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
import src.tools as tools

class Mapper:
    def __init__(self, label, fn_map=None, key=None):
        self.label = label
        self._fn  = fn_map if fn_map else lambda x: x
        self._dat = []
        self._k   = key

    def collect(self, x):
        # collection of iterable type
        if type(self._at(x)) is type([]):
            self._dat += map(self._fn, self._at(x))
            return
        # collection of scalar
        self._dat.append(self._fn(self._at(x)))

    def data(self):
        return self._dat

    def clear(self):
        self._dat = []

    def _at(self, x):
        return x if not self._k else x[self._k]


class Aggregator(Mapper):
    def __init__(self, label, fn_map=lambda x: x, fn_red=None, fn_agg=None, key=None):
        Mapper.__init__(self, label, fn_map, key)
        self._fn_red = fn_red
        self._fn_agg = fn_agg

    def reduce(self):
        if not self._fn_red:
            return None
        return functools.reduce(self._fn_red, self._dat)

    def aggregate(self):
        if not self._fn_agg:
            return self._dat
        self._dat = list(self._fn_agg(self._dat))
        return self._dat


class EnrichmentPipeline():
    def __init__(self, enrichers=[]):
        for ce in enrichers:
            assert type(ce) == Aggregator
        self.enrichers = enrichers

    # add comment to every enricher's collection
    def collect_all(self, comments):
        # TODO: zipped multiple different parameters (as lists)
        for c in comments:
            for e in self.enrichers:
                e.collect(c)

    # have every enricher process aggregate of comments, if defined
    def aggregate_all(self):
        # TODO: zipped multiple different parameters (as lists)
        for e in self.enrichers:
            e.aggregate()

    # have every enricher store internally-dumped data to external source
    def store_all(self, comments):
        for c, i in zip(comments, range(len(comments))):
            for e in self.enrichers:
                c[e.label] = e.data()[i]

    # clears data
    def clear_all(self):
        for e in self.enrichers:
            e.clear()


'''
pre-defined aggregator examples
'''
ZSCORE_AGGREGATOR = Aggregator(label='zscore',
                               fn_map=None,
                               fn_red=None,
                               fn_agg=stats.zscore,
                               key='score')

# more complex since an external model is required
def get_entities(element):
    spacy_nlp = spacy.load('en')
    entities = spacy_nlp(element).ents
    return [{item.label_: item.text} for item in entities]

ENTITIES_AGGREGATOR = Aggregator(label='entities',
                                 fn_map=get_entities,
                                 fn_red=None,
                                 fn_agg=None,
                                 key='body')

# more complex since an external model is required
def afinn_elementwise(element):
    afinn_nlp = afinn.Afinn(language='en', emoticons=True)
    return afinn_nlp.score(element)

AFINN_AGGREGATOR = Aggregator(label='afinn_score',
                              fn_map=afinn_elementwise,
                              fn_red=None,
                              fn_agg=None,
                              key='body')

# ensure data is valid for pipeline enrichment
def validate(data):
    # verify type
    assert data and type(data) == list, 'unexpected input type: {0}'.format(type(data))
    # verify structure integrity
    assert data[0]['id']
    assert type(data[0]['score']) == int
    assert len(data[0]['comments']) > 0

# pipeline enrichment that accepts Aggregator objects to define pipeline
def enrich(path, enrichers=[]):
    data = tools.load_json(path)
    # validation step, begin work after
    #validate(data)
    # TODO: deal w submission enrichers later...
    pipeline = EnrichmentPipeline(enrichers)
    # enrich data
    pipeline.collect_all(data)
    pipeline.aggregate_all()
    pipeline.store_all(data)
    pipeline.clear_all()
    '''for submission in data:
        # collect all comments
        pipeline.collect_all(submission['comments'])
        # aggregate all
        pipeline.aggregate_all()
        # save resultant data
        pipeline.store_all(submission['comments'])
        # clear
        pipeline.clear_all()'''
    # ZSCORE_AGGREGATOR.collect({'score':5})
    # ENTITIES_AGGREGATOR.collect({'body':'United States, Human, John Adams'})
    # print(ZSCORE_AGGREGATOR.label, ZSCORE_AGGREGATOR.data())
    # print(ENTITIES_AGGREGATOR.label, ENTITIES_AGGREGATOR.data())

    return data

def enrich_test(path):
    return enrich(path, enrichers=[ZSCORE_AGGREGATOR, ENTITIES_AGGREGATOR, AFINN_AGGREGATOR])
