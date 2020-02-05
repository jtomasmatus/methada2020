import pycompass
from pycompass.query import run_query


class Connect:

    def __init__(self, url, username=None, password=None):
        '''
        Connect class is used to get a connection to a valid COMPASS GraphQL endpoint. If username and password are
        provided, it will be possible to store and manage Modules on the server

        :param url: the COMPASS GraphQL endpoint URL
        :param username: the username
        :param password: the password
        '''

        self.url = url
        self.__token__ = None
        self.username = username
        self.password = password
        self.login(username, password)

    def login(self, username=None, password=None):
        '''
        Login

        :param username:
        :param password:
        :return:
        '''

        self.username = username
        self.password = password
        if self.username and self.password:
            self.__token__ = self.__get_token__()

    def signup(self, username=None, email=None, password=None):
        '''
        Signup as new user

        :param username: the username
        :param email: the user email
        :param password: the password
        :return: ok if the user has been added
        '''
        query = '''\
            mutation {{\
                {base}(username:"{username}", email:"{email}", password:"{password}") {{\
                    {fields}\
                }}\
            }}\
        '''.format(base='signup',
                   username=username,
                   email=email,
                   password=password,
                   fields='ok'
                   )
        json = run_query(self.url, query)
        self.login(username, password)
        return True

    def get_compendium(self, name):
        '''
        Get a compendium by a given name, None otherwise

        :param name: the compendium name
        :return: Compendium object
        '''
        for c in self.get_compendia():
            if c.compendium_name == name:
                return c
        return None

    def get_compendia(self):
        '''
        Get all available compendia

        :return: list of Compendium objects
        '''
        query = '''{
          compendia {
            name,
            fullName,
            description,
            normalization
          }
        }'''
        json = run_query(self.url, query)
        compendia = []
        for c in json['data']['compendia']:
            comp = pycompass.Compendium.__factory_build_object__(
                compendium_name=c['name'],
                connection=self,
                compendium_full_name=c['fullName'],
                description=c['description'],
                normalization=c['normalization']
            )
            compendia.append(comp)
        return compendia

    def __get_token__(self):
        query = '''\
            mutation {{\
                tokenAuth(username: "{}", password: "{}") {{\
                    token\
                }}\
            }}\
        '''.format(self.username, self.password)
        json = run_query(self.url, query)
        return json['data']['tokenAuth']['token']
