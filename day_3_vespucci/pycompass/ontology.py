from pycompass.query import query_getter
from pycompass.utils import get_compendium_object
import json


class Ontology:

    def __init__(self, *args, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
        self.__structure__ = None

    def by(self, *args, **kwargs):
        raise NotImplementedError()

    def get(self, filter=None, fields=None):
        '''
        Get the ontology used to annotate samples and biological features

        :param filter: return results that match only filter values
        :param fields: return only specific fields
        :return: list of Ontology objects
        '''
        @query_getter('ontology', ['id', 'name'])
        def _get_ontology(obj, filter=None, fields=None):
            pass
        return [Ontology(**dict({'compendium': self.compendium}, **o)) for o in _get_ontology(self.compendium, filter=filter, fields=fields)]

    @property
    def structure(self):
        '''
        Get the whole ontology hierarchy structure

        :param
        :return: ontology structure in node-link format
        '''
        if not self.__structure__:
            @query_getter('ontology', ['structure'])
            def _get_ontology_hierarchy(obj, filter=None, fields=None):
                pass
            os = _get_ontology_hierarchy(self.compendium, filter={'name': self.name})
            self.__structure__ = json.loads(os[0]['structure'])
        return self.__structure__


    @staticmethod
    def using(compendium):
        cls = get_compendium_object(Ontology)
        return cls(compendium=compendium)
