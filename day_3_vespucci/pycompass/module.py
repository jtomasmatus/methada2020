from pycompass.biological_feature import BiologicalFeature
from pycompass.query import query_getter, run_query
from pycompass.sample_set import SampleSet
from pycompass.utils import get_compendium_object
import numpy as np
import pickle as pk


class Module:

    def __init__(self, *args, **kwargs):
        self.biological_features = []
        self.sample_sets = []
        self.name = None
        self.id = None
        self.__normalized_values__ = None
        for k, v in kwargs.items():
            setattr(self, k, v)

    def by(self, *args, **kwargs):
        raise NotImplementedError()

    def get(self, filter=None, fields=None):
        '''
        Get modules

        :param filter: return results that match only filter values
        :param fields: return only specific fields
        :return: list of Module objects
        '''
        @query_getter('searchModules', ['id', 'name'])
        def _get_modules(obj, filter=None, fields=None):
            pass

        def _get_module_details(compendium, name):
            headers = {"Authorization": "JWT " + compendium.connection.__token__}
            query = '''\
                        {{\
                            {base}(compendium:"{compendium}", name:{name}) {{\
                                {fields}\
                            }}\
                        }}\
                    '''.format(base='modules', compendium=compendium.compendium_name, name='"' + name + '"',
                               fields='normalizedValues, ' +
                                'biofeatures {' +
                                'edges {' +
                                'node {' +
                                'id } } }' +
                                'sampleSets {' +
                                'edges {' +
                                'node {' +
                                'id } } }'
                               )
            json = run_query(compendium.connection.url, query, headers=headers)
            if 'errors' in json:
                raise Exception('Module {} does not exist'.format(name))
            bio_features = [e['node']['id'] for e in json['data']['modules']['biofeatures']['edges']]
            sample_sets = [e['node']['id'] for e in json['data']['modules']['sampleSets']['edges']]
            return bio_features, sample_sets

        modules = []
        for m in _get_modules(self.compendium, filter=filter, fields=fields):
            module = Module(**dict({'compendium': self.compendium}, **m))
            _bf, _ss = _get_module_details(self.compendium, module.name)
            module.sample_sets = SampleSet.using(self.compendium).get(filter={'id_In': str(_ss)})
            module.biological_features = BiologicalFeature.using(self.compendium).get(filter={'id_In': str(_bf)})
            module.rank = None
            module.normalization = module.sample_sets[0].normalization
            modules.append(module)
        return modules

    def delete(self):
        '''
        Delete current module from the server

        :return: boolean
        '''
        headers = {"Authorization": "JWT " + self.compendium.connection.__token__}
        query = '''\
                    mutation {{\
                        {base}(compendium:"{compendium}", name:"{name}") {{\
                            ok\
                        }}\
                    }}\
        '''.format(base='deleteModule', compendium=self.compendium.compendium_name,
                   name=self.name,
                   fields='ok'
                   )
        run_query(self.compendium.connection.url, query, headers=headers)
        self.biological_features = []
        self.sample_sets = []
        self.name = None
        self.id = None
        self.__normalized_values__ = None
        return True

    def update_name(self, new_name):
        '''
        Update current module's name

        :return: boolean
        '''
        headers = {"Authorization": "JWT " + self.compendium.connection.__token__}
        query = '''\
                    mutation {{\
                        {base}(compendium:"{compendium}", oldName:"{old_name}", newName:"{new_name}") {{\
                            ok\
                        }}\
                    }}\
        '''.format(base='updateModuleName', compendium=self.compendium.compendium_name,
                   old_name=self.name,
                   new_name=new_name,
                   fields='ok'
                   )
        run_query(self.compendium.connection.url, query, headers=headers)
        self.name = new_name
        return True

    def write_to_file(self, filename):
        '''
        Dump a module into a local file

        :param filename:
        :return:
        '''
        obj = {
            'bfs': [bf.id for bf in self.biological_features],
            'sss': [ss.id for ss in self.sample_sets],
            'id': self.id,
            'name': self.name,
            'normalization': self.normalization,
            'compendium': self.compendium.compendium_name,
            'values': self.values
        }
        with open(filename, 'wb') as fo:
            pk.dump(obj, fo)

    @staticmethod
    def read_from_file(filename, conn):
        '''
        Read module data from a local file

        :param filename:
        :return:
        '''
        module = Module()
        with open(filename, 'rb') as fi:
            obj = pk.load(fi)
            if obj:
                for c in conn.get_compendia():
                    if c.compendium_name == obj['compendium']:
                        module.compendium = c
                        break
                module.biological_features = BiologicalFeature.using(module.compendium).get(filter={'id_In': obj['bfs']})
                module.sample_sets = SampleSet.using(module.compendium).get(filter={'id_In': obj['sss']})
                module.name = obj['name']
                module.id = obj['id']
                module.normalization = obj['normalization']
                module.__normalized_values__ = obj['values']
        return module

    def save(self, name=None):
        '''
        Save a module on the server

        :param name: the module name
        :return: boolean
        '''
        if name is not None:
            self.name = name
        headers = {"Authorization": "JWT " + self.compendium.connection.__token__}
        query = '''\
            mutation {{\
                {base}(compendium:"{compendium}", name:{name}, biofeaturesIds:[{biofeaturesIds}], samplesetIds:[{samplesetIds}]) {{\
                    {fields}\
                }}\
            }}\
        '''.format(base='saveModule', compendium=self.compendium.compendium_name,
                   name='"' + self.name + '"',
                   biofeaturesIds=','.join(['"' + bf.id + '"' for bf in self.biological_features]),
                   samplesetIds=','.join(['"' + ss.id + '"' for ss in self.sample_sets]),
                   fields='ok, id'
                   )
        json = run_query(self.compendium.connection.url, query, headers=headers)
        self.id = json['data']['saveModule']['id']
        return True

    def create(self, biofeatures=None, samplesets=None, rank=None, cutoff=None, normalization=None):
        '''
        Create a new module

        :param biofeatures: the biofeatures list for the module (inferred if None)
        :param samplesets: the samplesets list for the module (inferred if None)
        :param rank: the rank method to be used for the inference
        :param cutoff: the cutoff to be used for the inference
        :param normalization: the normalization to be used for the inference
        :return: a Module object
        '''
        _bf_limit = 50
        _ss_limit = 50
        self.biological_features = biofeatures
        self.sample_sets = samplesets
        self.name = None
        self.id = None
        self.normalization = normalization
        # check that everything is ok to retrieve the normalized values
        if not self.biological_features and not self.sample_sets:
            raise Exception('You need to provide at least biofeatures or samplesets')
        elif self.biological_features is None:
            norm = None
            for ss in self.sample_sets:
                if ss.normalization and norm is None:
                    norm = ss.normalization
                if ss.normalization != norm:
                    raise Exception('You cannot mix SampleSets with different normalization')
            setattr(self, 'normalization', norm)
            all_ranks = self.compendium.normalization[self.normalization]['scoreRankMethods']['biologicalFeatures']
            _rank = rank
            if not rank:
                _rank = all_ranks[0]
            else:
                if rank not in all_ranks:
                    raise Exception('Invalid rank: choises are ' + ','.join(all_ranks))
            setattr(self, 'rank', _rank)
            # get first _bf_limit biofeatures automatically
            _bf = self.compendium.rank_biological_features(self, rank_method=_rank, cutoff=cutoff)
            _bf = _bf['ranking']['id'][:_bf_limit]
            self.biological_features = BiologicalFeature.using(self.compendium).get(
                filter={'id_In': str(_bf)}
            )
        elif self.sample_sets is None:
            if normalization:
                setattr(self, 'normalization', normalization)
            else:
                setattr(self, 'normalization', list(self.compendium.normalization.keys())[0])
            all_ranks = self.compendium.normalization[self.normalization]['scoreRankMethods']['sampleSets']
            _rank = rank
            if not rank:
                _rank = all_ranks[0]
            else:
                if rank not in all_ranks:
                    raise Exception('Invalid rank: choises are ' + ','.join(all_ranks))
            setattr(self, 'rank', _rank)
            # get first _ss_limit samplesets automatically
            _ss = self.compendium.rank_sample_sets(self, rank_method=_rank, cutoff=cutoff)
            _ss = _ss['ranking']['id'][:_ss_limit]
            self.sample_sets = SampleSet.using(self.compendium).get(
                filter={'id_In': str(_ss)}
            )
        # now we biofeatures and samplesets
        setattr(self, '__normalized_values__', None)
        self.values

        if self.normalization is None:
            for ss in self.sample_sets:
                if ss.normalization:
                    self.normalization = ss.normalization
                    break

        return self

    @property
    def values(self):
        '''
        Get module values

        :return: np.array
        '''
        def _get_normalized_values(filter=None, fields=None):
            query = '''\
                {{\
                    {base}(compendium:"{compendium}" {filter}) {{\
                        {fields}\
                    }}\
                }}\
            '''.format(base='modules', compendium=self.compendium.compendium_name,
                       filter=', biofeaturesIds:[' + ','.join(['"' + bf.id + '"' for bf in self.biological_features]) + '],' +
                            'samplesetIds: [' + ','.join(['"' + ss.id + '"' for ss in self.sample_sets]) + ']', fields=fields)
            return run_query(self.compendium.connection.url, query)

        if self.__normalized_values__ is None or len(self.__normalized_values__) == 0:
            response = _get_normalized_values(fields="normalizedValues")
            self.__normalized_values__ = np.array(response['data']['modules']['normalizedValues'])
        return self.__normalized_values__

    def add_biological_features(self, biological_features=[]):
        '''
        Add biological feature to the module

        :param biological_features: list of BioFeatures objects
        :return: None
        '''
        before = set(self.biological_features)
        after = set(self.biological_features + biological_features)
        if len(set.intersection(before, after)) != 0:
            self.__normalized_values__ = None
            self.biological_features = list(after)

    def add_sample_sets(self, sample_sets=[]):
        '''
        Add sample sets to the module

        :param sample_sets: list of SampleSet objects
        :return: None
        '''
        before = set(self.sample_sets)
        after = set(self.sample_sets + sample_sets)
        if len(set.intersection(before, after)) != 0:
            self.__normalized_values__ = None
            self.sample_sets = list(after)

    def remove_biological_features(self, biological_features=[]):
        '''
        Remove biological feature from the module

        :param biological_features: list of BioFeatures objects
        :return: None
        '''
        before = set(self.biological_features)
        after = set(self.biological_features) - set(biological_features)
        if len(set.intersection(before, after)) != 0:
            self.__normalized_values__ = None
            self.biological_features = list(after)

    def remove_sample_sets(self, sample_sets=[]):
        '''
        Remove sample sets from the module

        :param sample_sets: list of SampleSet objects
        :return: None
        '''
        before = set(self.sample_sets)
        after = set(self.sample_sets) - set(sample_sets)
        if len(set.intersection(before, after)) != 0:
            self.__normalized_values__ = None
            self.sample_sets = list(after)

    @staticmethod
    def union(first, second, biological_features=True, sample_sets=True):
        '''
        Union of two modules

        :param first: first module
        :param second: second module
        :return: a new Module
        '''
        if not isinstance(first, Module) or not isinstance(second, Module):
            raise Exception('Arguments must be valid Module objects!')
        if first.compendium != second.compendium:
            raise Exception('Module objects must be from the same Compendium!')
        if first.normalization != second.normalization:
            raise Exception('Module objects must have the same normalization!')
        compendium = first.compendium
        normalization = first.normalization
        bf = set(first.biological_features)
        ss = set(first.sample_sets)
        if biological_features:
            bf = set.union(bf, set(second.biological_features))
            bf = list(bf)
        if sample_sets:
            ss = set.union(ss, set(second.sample_sets))
            ss = list(ss)
        m = Module()
        m.sample_sets = ss
        m.biological_features = bf
        m.compendium = compendium
        m.normalization = normalization
        m.rank = None
        m.values
        return m

    @staticmethod
    def intersection(first, second, biological_features=True, sample_sets=True):
        '''
        Intersection of two modules

        :param first: first module
        :param second: second module
        :return: a new Module
        '''
        if not isinstance(first, Module) or not isinstance(second, Module):
            raise Exception('Arguments must be valid Module objects!')
        if first.compendium != second.compendium:
            raise Exception('Module objects must be from the same Compendium!')
        if first.normalization != second.normalization:
            raise Exception('Module objects must have the same normalization!')
        compendium = first.compendium
        normalization = first.normalization
        bf = set(first.biological_features)
        ss = set(first.sample_sets)
        if biological_features:
            bf = set.intersection(bf, set(second.biological_features))
            bf = list(bf)
            if len(bf) == 0:
                raise Exception("There are no biological features in common between these two modules!")
        if sample_sets:
            ss = set.intersection(ss, set(second.sample_sets))
            ss = list(ss)
            if len(ss) == 0:
                raise Exception("There are no sample sets in common between these two modules!")
        m = Module()
        m.sample_sets = ss
        m.biological_features = bf
        m.compendium = compendium
        m.normalization = normalization
        m.rank = None
        m.values
        return m

    @staticmethod
    def difference(first, second, biological_features=True, sample_sets=True):
        '''
        Difference between two modules

        :param first: first module
        :param second: second module
        :return: a new Module
        '''
        if not isinstance(first, Module) or not isinstance(second, Module):
            raise Exception('Arguments must be valid Module objects!')
        if first.compendium.compendium_name != second.compendium.compendium_name:
            raise Exception('Module objects must be from the same Compendium!')
        if first.normalization != second.normalization:
            raise Exception('Module objects must have the same normalization!')
        compendium = first.compendium
        normalization = first.normalization
        bf = set([_bf.id for _bf in first.biological_features])
        ss = set([_ss.id for _ss in first.sample_sets])
        if biological_features:
            bf = set.difference(bf, set([_bf.id for _bf in second.biological_features]))
            bf = list(bf)
            if len(bf) == 0:
                raise Exception("There are no biological features in common between these two modules!")
        if sample_sets:
            ss = set.difference(ss, set([_ss.id for _ss in second.sample_sets]))
            ss = list(ss)
            if len(ss) == 0:
                raise Exception("There are no sample sets in common between these two modules!")
        m = Module()
        m.sample_sets = SampleSet.using(compendium).get(filter={'id_In': ss})
        m.biological_features = BiologicalFeature.using(compendium).get(filter={'id_In': bf})
        m.compendium = compendium
        m.normalization = normalization
        m.rank = None
        m.values
        return m

    def split_module_by_biological_features(self):
        '''
        Split the current module in different modules dividing the module in distinct groups of coexpressed biological features

        :return: list of Modules
        '''
        raise NotImplementedError()

    def split_module_by_sample_sets(self):
        '''
        Split the current module in different modules dividing the module in distinct groups of sample_sets
        showing similar values.

        :return: list of Modules
        '''
        raise NotImplementedError()

    @staticmethod
    def using(compendium):
        cls = get_compendium_object(Module)
        return cls(compendium=compendium)
