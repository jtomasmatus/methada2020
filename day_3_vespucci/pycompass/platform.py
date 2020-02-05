from pycompass.query import query_getter
from pycompass.utils import get_compendium_object


class Platform:

    def __init__(self, *args, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    def by(self, *args, **kwargs):
        raise NotImplementedError()

    def get(self, filter=None, fields=None):
        '''
        Get the technological platforms used in the experiments

        :param filter: return results that match only filter values
        :param fields: return only specific fields
        :return: list of dict
        '''
        @query_getter('platforms', ['id', 'platformAccessId', 'platformName', 'description',
                                'dataSource { id, sourceName, isLocal }',
                                'platformType { id, name, description }'])
        def _get_platform(obj, filter=None, fields=None):
            pass
        return [Platform(**dict({'compendium': self.compendium}, **plt)) for plt in _get_platform(self.compendium, filter=filter, fields=fields)]

    @staticmethod
    def using(compendium):
        cls = get_compendium_object(Platform)
        return cls(compendium=compendium)
