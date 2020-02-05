import json

from pycompass.query import query_getter
from pycompass.sample import Sample
from pycompass.utils import get_compendium_object


class SampleSet:
    def __init__(self, s=(), *args, **kwargs):
        self.__samples__ = tuple(s)
        self.__current__ = 0
        self.__len__ = len(self.__samples__)
        for k, v in kwargs.items():
            if k == 'normalizationdesignsampleSet':
                continue
            elif k == 'design':
                self.design = json.loads(v)
            else:
                setattr(self, k, v)

    def __iter__(self):
        self.__current__ = 0
        return self

    def __next__(self):
        if self.__current__ >= self.__len__:
            raise StopIteration
        else:
            self.__current__ += 1
            return Sample.using(self.compendium).get(filter={'id': self.__samples__[self.__current__ - 1]})[0]

    def by(self, *args, **kwargs):
        '''
        Get sample sets by using other objects
        Example:

        :return: list of SampleSet objects
        '''
        filter = {}
        if 'samples' in kwargs:
            filter['samples'] = [s.id for s in kwargs['samples']]
        if 'normalization' in kwargs:
            filter['normalization'] = kwargs['normalization']
        return self.get(filter=filter)

    def get(self, filter=None, fields=None):
        '''
        Get the sample sets

        :param filter: return results that match only filter values
        :param fields: return only specific fields
        :return: list of SampleSet objects
        '''
        @query_getter('sampleSets', ['id',
                                     'name',
                                     'design',
                                     'normalization',
                                     'normalizationdesignsampleSet { edges { node { sample { id } } } }'])
        def _get_sample_sets(obj, filter=None, fields=None):
            pass
        _ss = []
        for ss in _get_sample_sets(self.compendium, filter=filter, fields=fields):
            samples = [s['node']['sample']['id'] for s in ss['normalizationdesignsampleSet']['edges']]
            _ss.append(SampleSet(s=samples, **dict({'compendium': self.compendium}, **ss)))

        return _ss

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        return self.id == other.id

    @staticmethod
    def using(compendium):
        cls = get_compendium_object(SampleSet)
        return cls(compendium=compendium)
