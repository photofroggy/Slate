''' slate.core
    core application object.
    Created by photofroggy.
'''


import sys
import time
import platform
from twisted.internet import reactor

from stutter import logging
from reflex.control import EventManager
from reflex.control import RulesetBattery
from reflex.control import ReactorBattery

from slate.users import UserManager
from slate.custom import Client
from slate.custom import ChannelLogger
from slate.config import Settings
from slate.config import Configure

from slate import rules
import extensions


class Bot(object):
    
    class platform:
        """ Information about the slate platform. """
        name = 'Slate'
        version = 1
        state = 'Alpha (repo)'
        build = 2
        stamp = '11122011-032934'
        series = 'Chip'
        author = 'photofroggy'
    
    config = None
    log = None
    client = None
    events = None
    agent = None
    
    debug = False
    restartable = False
    close = False
    restart = False
    
    def __init__(self, debug=False, restartable=True):
        self.platform.stamp = time.strftime('%d%m%Y-%H%M%S')
        self.debug = debug
        self.restartable = restartable
        
        logging.LEVEL.MESSAGE+= logging.LEVEL.WARNING
        logging.LEVEL.WARNING = logging.LEVEL.MESSAGE - logging.LEVEL.WARNING
        logging.LEVEL.MESSAGE-= logging.LEVEL.WARNING
        
        self.populate_objects()
        
        if debug:
            self.log.set_level(logging.LEVEL.DEBUG)
        
        self.log.start()
        
        self.hello()
        
        self.set_agent()
        
        self.start_configure()
    
    def populate_objects(self):
        self.config = Settings()
        self.log = ChannelLogger(stdout=self.write, default_sns=False)
        self.users = UserManager(stdout=self.log.message, stddebug=self.log.debug)
        self.users.load()
        self.events = EventManager(stdout=self.log.message, stddebug=self.log.debug)
        self.client = Client(
            stdout=self.log.message,
            stddebug=self.log.debug,
            _events=self.events,
            _teardown=self.teardown,
        )
        self.rules = RulesetBattery(stdout=self.log.message, stddebug=self.log.debug)
        self.exts = ReactorBattery(stdout=self.log.message, stddebug=self.log.debug)
        self.rules.load_objects(self.events, rules, core=self)
        self.exts.load_objects(self.events, extensions, 'Extension', self)
    
    
    def start_configure(self):
        self.config.load()
        
        if self.config.api.username is None:
            c=Configure(
                reactor,
                '198', 'f1e3ec71552293b5b82509c90836778d',
                agent=self.agent,
                stdout=self.log.message,
                stddebug=self.log.debug
            )
            
            if c.d is not None:
                c.d.addCallback(self.configured)
                reactor.run()
                return
        
        self.configured({'status': True, 'response': None})
    
    def set_agent(self):
        uname = platform.uname()
        release, name, version = uname[:3]
        self.agent = 'slate/{0}/{1}.{2} (dAmnViper/{3}/{4}.{5}; reflex/{6}/{7}.{8}; stutter/1) {9} {10}'.format(
            self.platform.stamp,
            self.platform.version,
            self.platform.build,
            self.client.platform.stamp,
            self.client.platform.version,
            self.client.platform.build,
            self.events.info.stamp,
            self.events.info.version,
            self.events.info.build,
            '({0}; U; {1} {2}; en-GB; {3}) '.format(name, release, version, self.config.owner),
            'Python/{0}.{1}'.format(sys.version_info[0], sys.version_info[1] )
        )
        
        self.client.agent = self.agent
    
    def hello(self):
        """ Greet the user, dawg. """
        self.log.message('** Welcome to {0} {1}.{2} {3}!'.format(
            self.platform.name,
            self.platform.version,
            self.platform.build,
            self.platform.state
        ), showns=False)
        self.log.message('** Created by photofroggy.', showns=False)
    
    def configured(self, response):
        self.config.load()
        
        if response['status'] is False or self.config.api.username is None:
            self.teardown()
            return False
        
        self.client.user.username = self.config.api.username
        self.client.user.token = self.config.api.damntoken
        self.client.autojoin = self.config.autojoin
        self.client.owner = self.config.owner
        self.client.trigger = self.config.trigger
        
        self.users.load(owner=self.config.owner)
        
        self.client.start()
        
        try:
            reactor.run()
        except Exception:
            pass
    
    def teardown(self):
        self.close = self.client.flag.close
        self.restart = self.client.flag.restart
        
        try:
            reactor.stop()
        except Exception:
            pass
        
        self.log.message('** Exiting...', showns=False)
        self.log.stop()
        self.log.push(0)
    
    def write(self, msg, *args, **kwargs):
        try:
            sys.stdout.write(msg)
            sys.stdout.flush()
        except Exception as e:
            self.log.warning('>> Failed to display a message...', showns=False)
        


# EOF
