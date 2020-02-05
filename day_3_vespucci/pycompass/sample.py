from pycompass.experiment import Experiment
from pycompass.platform import Platform
from pycompass.query import query_getter
from pycompass.utils import get_compendium_object


class Sample:

    def __init__(self, *args, **kwargs):
        for k, v in kwargs.items():
            if k == 'experiment':
                self.__experiment_id__ = v['id']
            elif k == 'platform':
                self.__platform_id__ = v['id']
            else:
                setattr(self, k, v)

    @property
    def experiment(self):
        return Experiment.using(self.compendium).get(filter={'id': self.__experiment_id__})[0]

    @property
    def platform(self):
        return Platform.using(self.compendium).get(filter={'id': self.__platform_id__})[0]

    def by(self, *args, **kwargs):
        '''
        Get samples by using another object
        Example: Sample.using(compendium).by(platform=plt)

        :return: list of Sample objects
        '''
        if 'experiment' in kwargs:
            filter = {'experiment_ExperimentAccessId': kwargs['experiment'].experimentAccessId}
            return self.get(filter=filter)
        elif 'platform' in kwargs:
            filter = {'platform_PlatformAccessId': kwargs['platform'].platformAccessId}
            return self.get(filter=filter)
        else:
            return []

    def get(self, filter=None, fields=None):
        '''
        Get compendium samples

        :param filter: return results that match only filter values
        :param fields: return only specific fields
        :return: list of Sample objects
        '''
        @query_getter('samples', ['id', 'sampleName', 'description', 'platform { id, platformAccessId }',
                                         'experiment { id, experimentAccessId }'])
        def _get_samples(obj, filter=None, fields=None):
            pass
        return [Sample(**dict({'compendium': self.compendium}, **e)) for e in _get_samples(self.compendium, filter=filter, fields=fields)]

    @staticmethod
    def using(compendium):
        cls = get_compendium_object(Sample)
        return cls(compendium=compendium)
