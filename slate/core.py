''' slate.core
    core application object.
    Created by photofroggy.
'''


import sys
from twisted.internet import reactor

from stutter import logging
from reflex.control import EventManager

from slate.users import UserManager
from slate.custom import Client
from slate.custom import ChannelLogger
from slate.config import Settings
from slate.config import Configure


class Bot(object):
    
    class platform:
        """ Information about the slate platform. """
        name = 'slate'
        version = 1
        state = 'Alpha'
        build = 1
        stamp = 'ddmmyyyy-hhmmss'
        series = 'Chip'
        author = 'photofroggy'
    
    config = None
    logger = None
    client = None
    events = None
    agent = None
    
    debug = False
    restartable = False
    close = True
    restart = False
    
    def __init__(self, debug=False, restartable=True):
        self.debug = debug
        self.restartable = restartable
        
        logging.LEVEL.MESSAGE+= logging.LEVEL.WARNING
        logging.LEVEL.WARNING = logging.LEVEL.MESSAGE - logging.LEVEL.WARNING
        logging.LEVEL.MESSAGE-= logging.LEVEL.WARNING
        
        self.populate_objects()
        
        if debug:
            self.logger.set_level(logging.LEVEL.DEBUG)
        
        self.logger.start()
        
        self.agent = 'slate/{0}/{1}.{2} (dAmnViper/{3}/{4}.{5}; reflex/1; stutter/1) OS'.format(
            self.platform.stamp,
            self.platform.version,
            self.platform.build,
            self.client.platform.stamp,
            self.client.platform.version,
            self.client.platform.build
        )
        
        self.client.agent = self.agent
        
        self.start_configure()
    
    def populate_objects(self):
        self.config = Settings()
        self.logger = ChannelLogger(stdout=self.write)
        self.users = UserManager(stdout=self.logger.message, stddebug=self.logger.debug)
        self.events = EventManager(stdout=self.logger.message, stddebug=self.logger.debug)
        self.client = Client(
            stdout=self.logger.message,
            stddebug=self.logger.debug,
            _events=self.events
        )
    
    def start_configure(self):
        self.config.load()
        
        if self.config.api.username is None:
            c=Configure(
                reactor,
                '110', '605c4a06216380fbdff26228c53cf610',
                agent=self.agent,
                stdout=self.logger.message,
                stddebug=self.logger.debug
            )
            c.d.addCallback(self.configured)
            c.d.addErrback(self.noncon)
            return
        
        self.configured({})
    
    def configured(self, response):
        self.config.load()
        if self.config.api.username is None:
            return False
        
        self.client.user.username = self.config.api.username
        self.client.user.token = self.config.api.damntoken
        self.client.autojoin = self.config.autojoin
        self.client.owner = self.config.owner
        self.client.trigger = self.config.trigger
        
        self.users.load(owner=self.config.owner)
        
        self.client.start()
        reactor.run()
        
        self.logger.stop()
        self.logger.push(0)
    
    def noncon(self, response):
        self.logger.warning('Failed to retrieve login codes.', showns=False)
        self.logger.message('Exiting...', showns=False)
        self.logger.stop()
        self.logger.push(0)
    
    def write(self, msg, *args, **kwargs):
        try:
            sys.stdout.write(msg)
            sys.stdout.flush()
        except Exception as e:
            self.logger.warning('Failed to display a message...')
        


# EOF
