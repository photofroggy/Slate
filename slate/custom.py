''' slate.custom module
    Created by photofroggy
    
    Custom child objects.
'''


import os
import sys
import time
import os.path
from twisted.internet import reactor

from stutter import logging
from dAmnViper.base import dAmnClient


class ChannelLogger(logging.ThreadedLogger):
    """ Channel-concious logger.
        
        This logger hopefully manages to save logs for different channels in
        appropriate sub folders of the logging directory.
    """
    
    def __init__(self, default_ns=None, *args, **kwargs):
        super(ChannelLogger, self).__init__(save_folder='./storage/logs', *args, **kwargs)
        self.default_ns = default_ns or '~Global'
    
    def _fname(self, timestamp, ns=None, showns=True):
        """ Return a file name based on the given input. """
        ns = ns or self.default_ns
        cdir = '{0}/{1}'.format(self.save_folder, ns)
        
        if not os.path.exists(cdir):
            os.mkdir(cdir, 0o755)
        
        return '{0}/{1}.txt'.format(cdir, time.strftime('%Y-%m-%d', time.localtime(timestamp)))
    
    def _display(self, lower, message, timestamp, ns=None, showns=True):
        """ Display the message. """
        if lower:
            return
        
        ns = ns or self.default_ns
        mns = '{0}|'.format(ns) if showns else ''
        self.stdout('{0}{1}{2}\n'.format(self.time(timestamp), mns, message))


class Client(dAmnClient):
    
    def init(self, stddebug=None):
        if stddebug is None:
            def debug(*args, **kwargs):
                return
            self.debug = debug
            return
        else:
            self.debug = stddebug
            self.flag.debug = True
            
        self.default_ns = '~Global'
    
    def teardown(self):
        try:
            reactor.stop()
        except Exception:
            pass
        
    def logger(self, msg, ns=None, showns=True, mute=False, pkt=None, ts=None):
        """ Write output to stdout. """
        if mute:
            self.debug(msg, ns=ns, showns=showns)
            return
        
        self.stdout(msg, ns=ns, showns=showns)


# EOF