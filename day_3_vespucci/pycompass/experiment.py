from pycompass.query import query_getter
from pycompass.utils import get_compendium_object


class Experiment:

    def __init__(self, *args, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    def by(self, *args, **kwargs):
        raise NotImplementedError()

    def get(self, filter=None, fields=None):
        '''
        Get compendium experiments

        :param filter: return results that match only filter values
        :param fields: return only specific fields
        :return: list of Experiment objects
        '''
        @query_getter('experiments', ['id', 'organism', 'experimentAccessId', 'experimentName', 'scientificPaperRef',
                                  'description', 'comments', 'dataSource { id, sourceName, isLocal }'])
        def _get_experiments(obj, filter=None, fields=None):
            pass
        return [Experiment(**dict({'compendium': self.compendium}, **e)) for e in _get_experiments(self.compendium, filter=filter, fields=fields)]

    @staticmethod
    def using(compendium):
        cls = get_compendium_object(Experiment)
        return cls(compendium=compendium)
