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
from reflex.data import Event
from dAmnViper.base import dAmnClient

from slate.rules.command.data import Command


class ChannelLogger(logging.ThreadedLogger):
    """ Channel-concious logger.
        
        This logger hopefully manages to save logs for different channels in
        appropriate sub folders of the logging directory.
    """
    
    def __init__(self, default_ns=None, default_sns=True, *args, **kwargs):
        super(ChannelLogger, self).__init__(save_folder='./storage/logs', *args, **kwargs)
        self.default_ns = default_ns or '~Global'
        self.default_sns = default_sns
    
    def _fname(self, timestamp, ns=None, showns=None):
        """ Return a file name based on the given input. """
        ns = ns or self.default_ns
        if showns is None:
            showns = self.default_sns
        
        cdir = '{0}/{1}'.format(self.save_folder, ns)
        
        if not os.path.exists(cdir):
            os.mkdir(cdir, 0o755)
        
        return '{0}/{1}.txt'.format(cdir, time.strftime('%Y-%m-%d', time.localtime(timestamp)))
    
    def _display(self, lower, message, timestamp, ns=None, showns=None):
        """ Display the message. """
        if lower:
            return
        if showns is None:
            showns = self.default_sns
        if len(message) > 200:
            message = '>> Message too long. See log for details.'
        
        ns = ns or self.default_ns
        mns = '{0}|'.format(ns) if showns else ''
        self.stdout('{0}{1}{2}\n'.format(self.time(timestamp), mns, message))


class Client(dAmnClient):
    
    def init(self, stddebug=None, _events=None, _teardown=None):
        if stddebug is None:
            def debug(*args, **kwargs):
                return
            self.debug = debug
            return
        else:
            self.debug = stddebug
            self.flag.debug = True
            
        self.default_ns = '~Global'
        self._events = _events
        self._teardown = _teardown
        self.trigger = '!'
        self.owner = 'noone'
    
    def teardown(self):
        self._teardown()
        
    def logger(self, msg, ns=None, showns=True, mute=False, pkt=None, ts=None):
        """ Write output to stdout. """
        if mute:
            self.debug(msg, ns=ns, showns=showns)
            return
        
        ns = ns or self.default_ns
        
        try:
            if msg.startswith('** Got ') and self.channel[self.format_ns(ns)].member == {}:
                self.debug(msg, ns=ns, showns=showns)
                return
        except KeyError:
            pass
        
        self.stdout(msg, ns=ns, showns=showns)
    
    def pkt_generic(self, event):
        self._events.trigger(Event(event.name, event.arguments.items()), self)
    
    def pkt_recv_msg(self, event):
        if not event.arguments['message'].lower().startswith(self.trigger):
            return
        
        msg = event.arguments['message'][len(self.trigger):]
        cmd, sp, msg = msg.partition(' ')
        target = event.arguments['ns']
        
        if msg.startswith('#') or msg.startswith('@'):
            target, sp, msg = msg.partition(' ')
        
        event.arguments['trigger'] = cmd
        event.arguments['target'] = self.format_ns(target)
        event.arguments['message'] = msg
        
        cobj = Command('command', event.arguments.items())
        self._events.trigger(cobj, self)


# EOF