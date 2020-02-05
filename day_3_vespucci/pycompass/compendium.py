from operator import itemgetter

from pycompass.query import run_query, query_getter
import numpy as np

from pycompass.utils import get_factory


def new__init__(self, *args, **kwargs):
    raise ValueError('Compendium object should be created using Connect.get_compendium() or Connect.get_compendia() methods!')


class Compendium(metaclass=get_factory(new__init__)):

    def __init__(self, *args, **kwargs):
        self.compendium_name = kwargs['compendium_name']
        self.connection = kwargs['connection']
        self.compendium_full_name = kwargs['compendium_full_name']
        self.description = kwargs['description']
        self.normalization = {}
        for n in kwargs['normalization']:
            self.normalization[n] = self.__get_score_rank_methods__(n)

        return self

    def get_data_sources(self, filter=None, fields=None):
        '''
        Get the experiments data sources both local and public

        :param filter: return results that match only filter values
        :param fields: return only specific fields
        :return: list of dict
        '''
        @query_getter('dataSources', ['id', 'sourceName', 'isLocal'])
        def _get_data_sources(obj, filter=None, fields=None):
            pass
        return _get_data_sources(self, filter=filter, fields=fields)

    def get_platform_types(self, filter=None, fields=None):
        '''
        Get the platform types

        :param filter: return results that match only filter values
        :param fields: return only specific fields
        :return: list of dict
        '''
        @query_getter('platformTypes', ['id', 'name', 'description'])
        def _get_platform_types(obj, filter=None, fields=None):
            pass
        return _get_platform_types(self, filter=filter, fields=fields)

    def rank_sample_sets(self, module, rank_method=None, cutoff=None):
        '''
        Rank all sample sets on the module's biological features using rank_method

        :param rank_method:
        :param cutoff:
        :return:
        '''
        bf = [_bf.id for _bf in module.biological_features]
        query = '''
            {{
                ranking(compendium:"{compendium}", normalization:"{normalization}", rank:"{rank}", 
                        biofeaturesIds:[{biofeatures}]) {{
                            id,
                            name,
                            value
            }}
        }}
        '''.format(compendium=self.compendium_name, normalization=module.normalization, rank=rank_method,
                   biofeatures='"' + '","'.join(bf) + '"')
        json = run_query(self.connection.url, query)
        r = json['data']
        if cutoff:
            idxs = [i for i, v in enumerate(r['ranking']['value']) if v >= cutoff]
            r['ranking']['id'] = itemgetter(*idxs)(r['ranking']['id'])
            r['ranking']['name'] = itemgetter(*idxs)(r['ranking']['name'])
            r['ranking']['value'] = itemgetter(*idxs)(r['ranking']['value'])
        return r

    def rank_biological_features(self, module, rank_method=None, cutoff=None):
        '''
        Rank all biological features on the module's sample set using rank_method

        :param rank_method:
        :param cutoff:
        :return:
        '''
        ss = [ss.id for ss in module.sample_sets]
        query = '''
            {{
                ranking(compendium:"{compendium}", normalization:"{normalization}", rank:"{rank}", 
                        samplesetIds:[{sample_set}]) {{
                            id,
                            name,
                            value
            }}
        }}
        '''.format(compendium=self.compendium_name, normalization=module.normalization, rank=rank_method,
                   sample_set='"' + '","'.join(ss) + '"')
        json = run_query(self.connection.url, query)
        r = json['data']
        if cutoff:
            idxs = [i for i,v in enumerate(r['ranking']['value']) if v >= cutoff]
            r['ranking']['id'] = itemgetter(*idxs)(r['ranking']['id'])
            r['ranking']['name'] = itemgetter(*idxs)(r['ranking']['name'])
            r['ranking']['value'] = itemgetter(*idxs)(r['ranking']['value'])
        return r

    def get_score_rank_methods(self, normalization):
        '''
        Get all the available ranking methods for biological features and sample sets

        :param normalization:
        :return:
        '''
        return self.__get_score_rank_methods__(normalization)['scoreRankMethods']

    def __get_score_rank_methods__(self, normalization):
        query = '''
            {{
              scoreRankMethods(compendium:"{compendium}", normalization:"{normalization}") {{
                sampleSets,
                biologicalFeatures
              }}
            }}
        '''.format(compendium=self.compendium_name, normalization=normalization)
        json = run_query(self.connection.url, query)
        return json['data']
