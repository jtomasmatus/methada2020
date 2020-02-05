from pycompass.query import run_query


class Plot:

    def __init__(self, module):
        self.module = module
        self.plot_types = None

        query = '''
            {{
              plotName(compendium:"{compendium}", normalization:"{normalization}") {{
                distribution,
                heatmap,
                network
              }}
            }}
        '''.format(compendium=self.module.compendium.compendium_name, normalization=self.module.normalization)
        self.plot_types = run_query(self.module.compendium.connection.url, query)['data']['plotName']

    def plot_heatmap(self, plot_type=None, output_format='html', *args, **kwargs):
        '''
        Get the HTML or JSON code that plot module heatmaps

        :param plot_type: the plot type
        :param output_format: html or json
        :return: str
        '''
        if plot_type is None:
            plot_type = self.plot_types['heatmap'][0]
        if plot_type not in self.plot_types['heatmap']:
            raise Exception('Invalid plot type. Options are ' + ','.join(self.plot_types['heatmap']))
        _options = []
        for k, v in kwargs.items():
            _v = str(v)
            if type(v) == str:
                _v = '"' + str(v) + '"'
            elif type(v) == bool:
                _v = str(v).lower()
            _options.append(str(k) + ':' + _v)
        options = ',' if len(_options) > 0 else ''
        options += ','.join(_options)
        query = '''
            {{
                plotHeatmap(compendium:"{compendium}", plotType:"{plot_type}", biofeaturesIds:[{biofeatures}],
                samplesetIds:[{samplesets}] {options}) {{
                    {output}
                }}
            }}
        '''.format(compendium=self.module.compendium.compendium_name,
                   plot_type=plot_type,
                   output=output_format,
                   options=options,
                   biofeatures='"' + '","'.join([bf.id for bf in self.module.biological_features]) + '"',
                   samplesets='"' + '","'.join([ss.id for ss in self.module.sample_sets]) + '"')
        json = run_query(self.module.compendium.connection.url, query)
        return json['data']['plotHeatmap'][output_format]

    def plot_network(self, plot_type=None, output_format='html', *args, **kwargs):
        '''
        Get the HTML or JSON code that plot the module networks

        :param plot_type: the plot type
        :param output_format: html or json
        :return: str
        '''
        if plot_type is None:
            plot_type = self.plot_types['network'][0]
        if plot_type not in self.plot_types['network']:
            raise Exception('Invalid plot type. Options are ' + ','.join(self.plot_types['network']))
        _options = []
        for k, v in kwargs.items():
            _v = str(v)
            if type(v) == str:
                _v = '"' + str(v) + '"'
            elif type(v) == bool:
                _v = str(v).lower()
            _options.append(str(k) + ':' + _v)
        options = ',' if len(_options) > 0 else ''
        options += ','.join(_options)
        query = '''
            {{
                plotNetwork(compendium:"{compendium}", plotType:"{plot_type}", biofeaturesIds:[{biofeatures}],
                samplesetIds:[{samplesets}] {options}) {{
                    {output}
                }}
            }}
        '''.format(compendium=self.module.compendium.compendium_name,
                   plot_type=plot_type,
                   output=output_format,
                   options=options,
                   biofeatures='"' + '","'.join([bf.id for bf in self.module.biological_features]) + '"',
                   samplesets='"' + '","'.join([ss.id for ss in self.module.sample_sets]) + '"')
        json = run_query(self.module.compendium.connection.url, query)
        return json['data']['plotNetwork'][output_format]

    def plot_distribution(self, plot_type, output_format='html', *args, **kwargs):
        '''
        Get the HTML or JSON code that plot module distributions

        :param plot_type: the plot type
        :param output_format: html or json
        :return: str
        '''
        if plot_type is None:
            plot_type = self.plot_types['distribution'][0]
        if plot_type not in self.plot_types['distribution']:
            raise Exception('Invalid plot type. Options are ' + ','.join(self.plot_types['distribution']))
        _options = []
        for k, v in kwargs.items():
            _v = str(v)
            if type(v) == str:
                _v = '"' + str(v) + '"'
            elif type(v) == bool:
                _v = str(v).lower()
            _options.append(str(k) + ':' + _v)
        options = ',' if len(_options) > 0 else ''
        options += ','.join(_options)
        query = '''
            {{
                plotDistribution(compendium:"{compendium}", plotType:"{plot_type}", normalization:"{normalization}", biofeaturesIds:[{biofeatures}],
                samplesetIds:[{samplesets}] {options}) {{
                    {output}
                }}
            }}
        '''.format(compendium=self.module.compendium.compendium_name,
                   plot_type=plot_type,
                   output=output_format,
                   normalization=self.module.normalization,
                   options=options,
                   biofeatures='"' + '","'.join([bf.id for bf in self.module.biological_features]) + '"',
                   samplesets='"' + '","'.join([ss.id for ss in self.module.sample_sets]) + '"')
        json = run_query(self.module.compendium.connection.url, query)
        return json['data']['plotDistribution'][output_format]
