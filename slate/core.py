''' slate.core
    core application object.
    Created by photofroggy.
'''


import sys
from twisted.internet import reactor

from stutter import logging
from reflex.control import EventManager

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
        
        self.agent = 'slate/{0}.{1}/{2} (dAmnViper/{3}; reflex/1; stutter/1) OS'.format(
            self.platform.version, self.platform.build, self.platform.stamp, self.client.platform.build
        )
        
        self.client.agent = self.agent
        
        if self.config.api.username is None:
            Configure(
                reactor,
                '110', '605c4a06216380fbdff26228c53cf610',
                agent=self.agent
            )
            self.config.load()
        
        self.client.user.username = self.config.api.username
        self.client.user.token = self.config.api.damntoken
        self.client.autojoin = self.config.autojoin
        
        self.client.start()
        reactor.run()
        
        self.logger.stop()
        self.logger.push(0)
    
    def populate_objects(self):
        self.config = Settings()
        self.logger = ChannelLogger(stdout=self.write)
        self.events = EventManager(stdout=self.logger.message, stddebug=self.logger.debug)
        self.client = Client(stdout=self.logger.message, stddebug=self.logger.debug)
    
    def write(self, msg):
        try:
            sys.stdout.write(msg)
            sys.stdout.flush()
        except Exception as e:
            self.logger.warning('Failed to display a message...')
        


# EOF
