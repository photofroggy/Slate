''' slate.config
    Created by photofroggy
    
    Manages the configuration for Slate.
'''

# stdlib
import os
import sys
import json
from twisted.internet import defer
from twisted.internet import reactor

from dAmnViper.dA.api import APIClient

# slate's stdlib
from slate.misc_lib import get_input
from slate.misc_lib import export_struct

class Settings:
    
    class api:
        def __init__(self):
            self.username = None
            self.symbol = None
            self.code = None
            self.token = None
            self.refresh = None
            self.damntoken = None
    
    owner = None
    trigger = None
    autojoin = None
    file = None
    
    def __init__(self, file='./storage/config.bsv'):
        self.file = file
        self.api = Settings.api()
        self.owner = None
        self.trigger = None
        self.autojoin = []
        self.load()
    
    def load(self):
        if not os.path.exists(self.file):
            return
        file = open(self.file, 'r')
        data = json.loads(file.read())
        file.close()
        # API data
        self.api.username = data['api']['username']
        self.api.symbol = data['api']['symbol']
        self.api.code = data['api']['code']
        self.api.token = data['api']['token']
        self.api.refresh = data['api']['refresh']
        self.api.damntoken = data['api']['damntoken']
        self.owner = data['owner']
        self.trigger = data['trigger']
        self.autojoin = data['autojoin']
    
    def save(self):
        data = {
            'api': {
                'username': str(self.api.username),
                'symbol': str(self.api.symbol),
                'code': str(self.api.code),
                'token': str(self.api.token),
                'refresh': str(self.api.refresh),
                'damntoken': str(self.api.damntoken)
            },
            'autojoin': self.autojoin,
            'owner': self.owner,
            'trigger': self.trigger
        }
        file = open(self.file, 'w')
        file.write(export_struct(data))
        file.close()

class Configure:
    
    # slate client id and secret
    # - id: 110
    # - secret: 605c4a06216380fbdff26228c53cf610
    file = './storage/config.bsv'
    
    def __init__(self, _reactor, id, secret, file='./storage/config.bsv', port=8080, agent='slate/1 (dAmnViper 2)', option=None, state=None, stdout=None, stddebug=None, cache='./storage/api.cache'):
        
        def default_write(msg, *args):
            pass
        
        self.stdout = stdout or default_write
        self._debug = stddebug or default_write
        self.d = None
        
        self.file = file
        self.cachef = cache
        if not os.path.exists('./storage'):
            os.mkdir('./storage', 0o755)
        self.write('** Welcome to the configuration file!')
        
        self.data = Settings(self.file)
        
        self.api = APIClient(_reactor, id, secret, self.data.api.code, self.data.api.token, agent)
        self.port = port
        self.state = state
        self._reactor = reactor
        
        if option is None or not self.data.api.username:
            self.run_all('http://localhost:{0}'.format(port))
        else:
            self.menu()
    
    def write(self, msg):
        self.stdout(msg, showns=False)
    
    def debug(self, msg):
        self._debug(msg, showns=False)
    
    def menu(self):
        while True:
            self.data.load()
            self.write('** Current configuration:')
            # Display config data!
            info = self.data.api
            self.write('** Bot {0} = {1}'.format('username', info.username))
            self.write('** Bot {0} = {1}'.format('owner', self.data.owner))
            self.write('** Bot {0} = {1}'.format('trigger', self.data.trigger))
            self.write('** Autojoin:')
            self.write(', '.join(self.data.autojoin))
            self.write('')
            self.write('** Choose one of the following options:')
            self.write('*** user - authorize the bot with a different account.')
            self.write('*** info - Set the bot\'s owner and trigger.')
            self.write('*** autojoin - Set the bot\'s autojoin list.')
            self.write('*** all - Set all configuration data.')
            self.write('*** exit - Leave the configuration file.')
            ins = ''
            
            while not ins in ('all', 'autojoin', 'exit', 'info', 'user'):
                ins = get_input('>> ').lower()
            
            if ins == 'exit':
                return
            
            if ins == 'all':
                self.run_all('http://localhost:{0}'.format(self.port))
                continue
            
            if ins == 'info':
                self.get_info()
                self.save()
                continue
            
            if ins == 'autojoin':
                self.get_autojoin()
                self.save()
            
            if ins == 'user':
                self.get_user('http://localhost:{0}'.format(self.port))
                
    
    def run_all(self, redirect):
        self.write('** Please fill in the following appropriately')
        self.get_info()
        self.get_autojoin()
        self.write('** Ok! Now we need to authorize!')
        return self.get_user(redirect)
    
    def get_user(self, redirect):
        try:
            file = open(self.cachef, 'r')
            cache = json.loads(file.read())
            file.close()
        except IOError:
            self.debug('>> No cache data stored')
            self.d = defer.Deferred()
            self.start_auth(redirect)
            return self.d
        
        user = get_input('> Bot account username: ')
        
        try:
            data = cache[user.lower()]
            self.data.api.username = data['username']
            self.data.api.symbol = data['symbol']
            self.data.api.code = data['code']
            self.data.api.token = data['token']
            self.data.api.refresh = data['refresh']
            self.data.api.damntoken = data['damntoken']
            self.debug('** Found cached data for {0}{1}.'.format(data['symbol'], data['username']))
            self.save()
        except KeyError:
            self.write('>> No cached data stored for \'{0}\''.format(user))
            self.write('>> Requires authorization')
            self.d = defer.Deferred()
            self.start_auth(redirect)
            return self.d
        
        return None
        
    
    def start_auth(self, redirect):
        """ Start the auth application.
            
            All this really does is start the auth server and then display a
            url on screen. The user should visit this url to authorize the app.
        """
        d = self.api.auth_app(self.port)
        d.addCallback(self.authResponse)
        # Make a url
        url = self.api.url('authorize', api='oauth2',
            client_id=self.api.client_id,
            client_secret=self.api.client_secret,
            redirect_uri=redirect,
            response_type='code',
            state=self.state
        )
        # Send user there, somehow...
        self.write('** Please visit the following URL to authorize this app:')
        sys.stdout.write('{0}\n'.format(url))
        sys.stdout.flush()
        # Now we wait for the user's webbrowser to be redirected to our server.
    
    def authResponse(self, response):
        """ Called when the app is successfully authorized. """
        if not response['status']:
            resp = response['data']
            
            if 'error' in resp.args:
                self.write('>> Auth failed: {0}\n'.format(resp.args['error_description'][0]))
            else:
                self.write('>> Authorization failed.\n')
                self.debug('>> {0}\n'.format(response['data']))
            
            self._reactor.stop()
            self.d.callback({'status': False, 'response': response})
            return response
        
        self.write('** Application authorized. Retrieving access token')
        
        self.data.api.code = self.api.auth_code
        self.data.save()
        d = self.api.grant(req_state=self.state)
        d.addCallbacks(self.grantResponse, self.grantFailure)
        
        return response
    
    def grantResponse(self, response):
        """ Called when the app is granted access to the API. """
        if not response['status']:
            self.write('>> Failed to get an access token.\n')
            
            try:
                self.write('>> {0}\n'.format(response['data'].data['error_description']))
            except KeyError:
                pass
            
            self._reactor.stop()
            self.d.callback({'status': False, 'response': response})
            return response
        
        self.write('** Got an access token!')
        self.data.api.token = self.api.token
        self.data.api.refresh = self.api.refresh_token
        self.data.save()
        # whoami?
        self.api.user_whoami().addCallback(self.whoami)
        return response
    
    def grantFailure(self, response):
        """ Called when the app is refused access to the API. """
        self.write('>> Failed to get an access token.')
        self._reactor.stop()
        self.d.callback({'status': False, 'response': response})
        return response
    
    def whoami(self, response):
        """ Handle the response to whoami API call. """
        
        if not 'username' in response.data:
            self.write('>> Whoami failed.')
            self._reactor.stop()
            self.d.callback({'status': False, 'response': response})
            return response
        
        symbol = response.data['symbol']
        username = response.data['username']
        self.data.api.symbol = symbol
        self.data.api.username = username
        self.data.save()
        self.write('** Authorized account {0}{1}'.format(symbol, username))
        self.api.user_damntoken().addCallback(self.damntoken)
    
    def damntoken(self, response):
        """ Handle the response to whoami API call. """
        
        if response.data is None:
            self.write('>> damntoken failed.')
            self.debug('>> debug data:')
            self.debug(response)
            self.d.callback({'status': False, 'response': response})
            return response
        
        self.data.api.damntoken = response.data['damntoken']
        self.write('** Retrieved authtoken')
        self.save()
        self.cache()
        self.d.callback({'status': True, 'response': response})
    
    def get_info(self):
        for option in ['owner', 'trigger']:
            setattr(self.data, option, get_input('> Bot ' + option + ': '))
    
    def get_autojoin(self):
        self.write( '** Next we need to know which channels you want your' )
        self.write( '** bot to join on startup. Please enter a list of' )
        self.write( '** channels below, separated by commas. Each channel' )
        self.write( '** must begin with a hash (#) or chat:. Leave blank' )
        self.write( '** to use the default (#Botdom).' )
    
        aj = get_input('> ', True)
        if aj:
            aj = aj.split(',')
            if aj:
                self.data.autojoin = [ns.strip() for ns in aj if ns.strip()]
        
        if not self.data.autojoin:
            self.data.autojoin.append('#Botdom')
    
    def save(self):
        self.data.save()
        
        self.write( '** Configuration file saved!' )
    
    def cache(self):
        try:
            file = open(self.cachef, 'r')
            cache = json.loads(file.read())
            file.close()
        except IOError:
            cache = {}
        
        cache[self.data.api.username.lower()] = {
                'username': self.data.api.username,
                'symbol': self.data.api.symbol,
                'code': self.data.api.code,
                'token': self.data.api.token,
                'refresh': self.data.api.refresh,
                'damntoken': self.data.api.damntoken
        }
        
        try:
            file = open(self.cachef, 'w')
            file.write(export_struct(cache))
            file.close()
        except IOError:
            pass

    
# EOF
