from unittest import TestCase

from pycompass.biological_feature import BiologicalFeature
from pycompass.experiment import Experiment
from pycompass.ontology import Ontology
from pycompass.platform import Platform
from pycompass.plot import Plot
from pycompass.sample import Sample
from pycompass.sample_set import SampleSet


class TestCompendium(TestCase):

    def test_all(self):
        from pycompass import Connect, Compendium, Module

        url = 'http://compass.fmach.it/graphql'
        conn = Connect(url)
        compendia = conn.get_compendia()

        ds = compendia[0].get_data_sources(fields=['sourceName'])
        
        plts = Platform.using(compendia[0]).get(fields=['platformAccessId'], filter={'first': 2})
        es = Experiment.using(compendia[0]).get(filter={'first': 1})
        s = Sample.using(compendia[0]).get(filter={'first': 10})
        se = s[0].experiment
        sp = s[0].platform
        s = Sample.using(compendia[0]).by(platform=plts[0])
        os = Ontology.using(compendia[0]).get(filter={'name': 'Gene ontology'})
        st = os[0].structure
        ss = SampleSet.using(compendia[0]).get(filter={'first': 2})
        ss = SampleSet.using(compendia[0]).by(samples=s[:1])
        bf = BiologicalFeature.using(compendia[0]).get(filter={'name_In': ['VIT_00s0332g00160', 'VIT_00s0396g00010', 'VIT_00s0505g00030']})
        mod1 = Module.using(compendia[0]).create(samplesets=ss)
        mod2 = Module.using(compendia[0]).create(biofeatures=bf)
        #mod1 = Module.using(compendia[0]).get(filter={'name': 'mod1'})[0]
        #mod2 = Module.using(compendia[0]).get(filter={'name': 'mod2'})[0]
        mod3 = Module.union(mod1, mod2)
        mod4 = Module.intersection(mod3, mod2)
        mod5 = Module.difference(mod1, mod2)
        html = Plot(mod1).plot_heatmap(alternativeColoring=True)
        html = Plot(mod1).plot_network()
        html = Plot(mod1).plot_distribution(plot_type='sample_sets_magnitude_distribution')
        pass

