from pycompass.query import query_getter
from pycompass.utils import get_compendium_object


class BiologicalFeature:

    def __init__(self, *args, **kwargs):
        for k, v in kwargs.items():
            if k == 'biofeaturevaluesSet':
                for n in v['edges']:
                    field = n['node']['bioFeatureField']['name']
                    value = n['node']['value']
                    setattr(self, field, value)
            else:
                setattr(self, k, v)

    def by(self, *args, **kwargs):
        raise NotImplementedError()

    def get(self, filter=None, fields=None):
        '''
        Get biological feature

        :param filter: return results that match only filter values
        :param fields: return only specific fields
        :return: list of BiologicalFeature objects
        '''
        @query_getter('biofeatures',
                      ['id', 'name', 'description', 'biofeaturevaluesSet { edges { node { bioFeatureField { name }, value } } }'])
        def _get_biological_features(obj, filter=None, fields=None):
            pass
        return [BiologicalFeature(**dict({'compendium': self.compendium}, **bf))
                for bf in _get_biological_features(self.compendium, filter=filter, fields=fields)]

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        return self.id == other.id

    @staticmethod
    def using(compendium):
        cls = get_compendium_object(BiologicalFeature)
        return cls(compendium=compendium)
