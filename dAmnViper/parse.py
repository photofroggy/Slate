''' dAmnViper.parse module
    Copyright (c) 2011, Henry "photofroggy" Rapley.
    Released under the ISC License.
    
    This module provides objects for parsing data going to and from the dAmn
    server. Tablumps and packets are handled by classes here, and a class is
    provided to generate output messages for stdout based on packets received
    from dAmn.
'''

import re
from collections import OrderedDict

class Packet(object):
    """ Use this class to parse dAmn packets.
        
        This object processes given strings as dAmn packets, and stores
        information from the string in different object attributes. This
        makes it easier to work with packets in other parts of the API.
    """

    def __init__(self, data=None, sep='='):
        self.cmd, self.param, self.args, self.body, self.raw = None, None, {}, None, data
        
        if not data:
            return
        
        data = data.partition('\n\n')
        self.body = data[2] or None
        data = data[0].partition('\n')
        
        if not data[0]:
            return
        
        if not sep in data[0]:
            head = data[0].partition(' ')
            self.cmd = head[0] or None
            self.param = head[2] or None
            data = data[2].partition('\n')
        
        while data[0]:
            arg = data[0].partition(sep)
            data = data[2].partition('\n')
            if not arg[1] or not arg[2]:
                continue
            self.args[arg[0]] = arg[2]
        
        # And that's the end of that chapter.
    
    def compile(self, sep='='):
        """ Return a plain text packet based on the packet's values. """
        if self.cmd is None:
            raise ValueError('Empty packet')
        
        args = '\n'.join([
            sep.join([key, value]) for key, value in self.args.iteritems() if value
        ]) or None
        
        return '{0}{1}\n{2}{3}'.format(
            self.cmd,
            '' if self.param is None else ' {0}'.format(self.param),
            '' if args is None else '{0}\n'.format(args),
            '' if self.body is None else '\n{0}'.format(self.body)
        )

class PacketEvent(object):
    """ Packet event.
        
        This object is a data structure which stores packet data under specific
        keys according to the mapping rules defined in the Protocol Parser.
    """
    
    def __init__(self, event, args=None):
        self.name = event
        self.arguments = OrderedDict() if args is None else OrderedDict(args)
    
    def __call__(self, argument, value=None):
        """ Shortcut for `.arg` and `.set_arg`. """
        
        if value is None:
            return self.arguments[argument]
        
        self.arguments[argument] = value
        return value


class Tablumps(object):
    """ dAmn tablumps parser.
        
        dAmn sends certain information formatted in a specific manner.
        Links, images, thumbs, and other forms of data are formatted
        in strings where the different attributes of these values are
        separated by tab characters (``\\t``), and usually begin with an
        ampersand.
        
        We refer to these items as "tablumps" because of the tab
        characters being used as delimeters. The job of this class is to
        replace tablumps with readable strings, or to extract the data
        given in the tablumps.
    """
    
    expressions = None
    replace = None
    titles = None
    subs = None
    
    def __init__(self):
        """Populate the expressions and replaces used when parsing tablumps."""
        if self.expressions is not None:
            return
        # Regular expression objects used to find any complicated tablumps.
        self.expressions = [
            re.compile("&avatar\t([a-zA-Z0-9-]+)\t([0-9]+)\t"),
            re.compile("&dev\t(.)\t([a-zA-Z0-9-]+)\t"),
            re.compile("&emote\t([^\t]+)\t([0-9]+)\t([0-9]+)\t(.*?)\t([a-z0-9./=-_]+)\t"),
            re.compile("&a\t([^\t]+)\t([^\t]*)\t"),
            re.compile("&link\t([^\t]+)\t&\t"),
            re.compile("&link\t([^\t]+)\t([^\t]+)\t&\t"),
            re.compile("&acro\t([^\t]+)\t(.*)&\/acro\t"),
            re.compile("&abbr\t([^\t]+)\t(.*)&\/abbr\t"),
            re.compile("&thumb\t(?P<ID>[0-9]+)\t([^\t]+)\t([^\t]+)\t([^\t]+)\t([^\t]+)\t([^\t]+)\t([^\t]+)\t"),
            re.compile("&img\t([^\t]+)\t([^\t]*)\t([^\t]*)\t"),
            re.compile("&iframe\t([^\t]+)\t([0-9%]*)\t([0-9%]*)\t&\/iframe\t"),
        ]
        self.titles = ('avatar', 'dev', 'emote', 'a', 'link', 'link', 'acronym', 'abbr', 'thumb', 'img', 'iframe')
        # Regular expression objects used to find and replace complicated tablumps.
        self.subs = [
            (re.compile("&avatar\t([a-zA-Z0-9-]+)\t([0-9]+)\t"), ":icon\\1:"),
            (re.compile("&dev\t(.)\t([a-zA-Z0-9-]+)\t"), ":dev\\2:"),
            (re.compile("&emote\t([^\t]+)\t([0-9]+)\t([0-9]+)\t(.*?)\t([a-z0-9./=-_]+)\t"), "\\1"),
            (re.compile("&a\t([^\t]+)\t([^\t]*)\t"), "<a href=\"\\1\" title=\"\\2\">"),
            (re.compile("&link\t([^\t]+)\t&\t"), "\\1"),
            (re.compile("&link\t([^\t]+)\t([^\t]+)\t&\t"), "\\1 (\\2)"),
            (re.compile("&acro\t([^\t]+)\t"), "<acronym title=\"\\1\">"),
            (re.compile("&abbr\t([^\t]+)\t"), "<abbr title=\"\\1\">"),
            (re.compile("&thumb\t([0-9]+)\t([^\t]+)\t([^\t]+)\t([^\t]+)\t([^\t]+)\t([^\t]+)\t([^\t]+)\t"), ":thumb\\1:"),
            (re.compile("&img\t([^\t]+)\t([^\t]*)\t([^\t]*)\t"), "<img src=\"\\1\" alt=\"\\2\" title=\"\\3\" />"),
            (re.compile("&iframe\t([^\t]+)\t([0-9%]*)\t([0-9%]*)\t&\/iframe\t"), "<iframe src=\"\\1\" width=\"\\2\" height=\"\\3\" />"),
            (re.compile("<([^>]+) (width|height|title|alt)=\"\"([^>]*?)>"), "<\\1\\3>"),
        ]
        # Search and replace pairs used to parse simple HTML tags.
        self.replace = [
            ("&b\t", "<b>"),
            ("&/b\t", "</b>"),
            ("&i\t", "<i>"),
            ("&/i\t", "</i>"),
            ("&u\t", "<u>"),
            ("&/u\t", "</u>"),
            ("&s\t", "<s>"),
            ("&/s\t", "</s>"),
            ("&sup\t", "<sup>"),
            ("&/sup\t", "</sup>"),
            ("&sub\t", "<sub>"),
            ("&/sub\t", "</sub>"),
            ("&code\t", "<code>"),
            ("&/code\t", "</code>"),
            ("&p\t", "<p>"),
            ("&/p\t", "</p>"),
            ("&ul\t", "<ul>"),
            ("&/ul\t", "</ul>"),
            ("&ol\t", "<ol>"),
            ("&/ol\t", "</ol>"),
            ("&li\t", "<li>"),
            ("&/li\t", "</li>"),
            ("&bcode\t", "<bcode>"),
            ("&/bcode\t", "</bcode>"),
            ("&br\t", "\n"),
            ("&/a\t", "</a>"),
            ("&/acro\t", "</acronym>"),
            ("&/abbr\t", "</abbr>"),
        ]
    
    def parse(self, data):
        """ Parse any dAmn Tablumps found in our input data.
            
            This method will simply return a string with the tablumps
            parsed into readable formats.
        """
        try:
            for lump, repl in self.replace:
                data = data.replace(lump, repl)
            for expression, repl in self.subs:
                data = expression.sub(repl, data)
        except Exception:
            pass
        return data
    
    def capture(self, text):
        """ Return any dAmn Tablumps found in our input data.
            
            Rather than parsing the tablumps, this method returns the
            data given by tablumps. This only works for tablumps where
            a regular expression is used for parsing.
        """
        lumps = {}
        for key, expression in enumerate(self.expressions):
            cc = expression.findall(text)
            if not cc:
                continue
            lumps[self.titles[key]] = cc
        return lumps

class ProtocolParser(object):
    """ Parser for processing the dAmn protocol.
        
        Use methods of this class to process dAmn information. You can
        customise how different packets are handled by adding items to
        protocol.maps and protocol.messages.
    """
    maps = {
        'dAmnServer': ['version'],
        'login': ['username', ['e'], 'data'],
        'join': ['ns', ['e'] ],
        'part': ['ns', ['e', '*r'] ],
        'property': ['ns', ['p', 'by', 'ts'], '*value' ],
        'recv_msg': [None, [('from', 'user')], '*message'],
        'recv_action': [None, [('from', 'user')], '*message'],
        'recv_join': ['user', None, '*info'],
        'recv_part': ['user', ['r']],
        'recv_privchg': ['user', ['by', 'pc']],
        'recv_kicked': ['user', ['by'], '*r'],
        'recv_admin_create': [None, ['p', ('by', 'user'), ('name', 'pc'), 'privs']],
        'recv_admin_update': [None, ['p', ('by', 'user'), ('name', 'pc'), 'privs']],
        'recv_admin_rename': [None, ['p', ('by', 'user'), 'prev', ('name', 'pc')]],
        'recv_admin_move': [None, ['p', ('by', 'user'), 'prev', ('name', 'pc'), ('n', 'affected')]],
        'recv_admin_remove': [None, ['p', ('by', 'user'), ('name', 'pc'), ('n', 'affected')]],
        'recv_admin_show': [None, ['p'], 'info'],
        'recv_admin_showverbose': [None, ['p'], 'info'],
        'recv_admin_privclass': [None, ['p', 'e'], 'command'],
        'kicked': ['ns', [('by', 'user')], '*r'],
        'ping': [],
        'disconnect': [None, ['e']],
        'send': ['ns', ['e']],
        'kick': ['ns', [('u', 'user'), 'e']],
        'get': ['ns', ['p', 'e']],
        'set': ['ns', ['p', 'e']],
        'kill': ['ns', ['e']],
        'unknown': [None, None, None, None, 'packet'],
    }
    names = [('recv', 'admin')]
    messages = {
        'dAmnServer': ('** Connected to dAmn Server {0}.', False),
        'login': ('** Login as {0}: {1}.', False),
        'join': ('** Join {ns}: "{1}".', False),
        'part': ('** Part {ns}: "{1}". [{2}]', False),
        'property': ('** Got {1} for {ns}.', False),
        'recv_msg': ('<{1}> {2}',),
        'recv_action': ('* {1} {2}',),
        'recv_join': ('** {1} has joined.',),
        'recv_part': ('** {1} has left. [{2}]',),
        'recv_privchg': ('** {1} has been made a member of {3} by {2} *',),
        'recv_kicked': ('** {1} has been kicked by {2} * {3}',),
        'recv_admin_create': ('** Privilege class {3} has been created by {2} with: {4}',),
        'recv_admin_update': ('** Privilege class {3} has been updated by {2} with: {4}',),
        'recv_admin_rename': ('** Privilege class {4} has been renamed to {3} by {2}',),
        'recv_admin_move': ('** All members of {3} have been moved to {4} by {2} -- {5} affected user(s)',),
        'recv_admin_remove': ('** Privilege class {3} has been removed by {2} -- {4} affected user(s)',),
        'recv_admin_show': None,
        'recv_admin_showverbose': None,
        'recv_admin_privclass': ('** Admin command "{2}" failed: {1}',),
        'kicked': ('** You have been kicked by {1} * {2}',),
        'ping': ('** Ping...', False, True),
        'disconnect': ('** You have been disconnected * {0}', False),
        'send': ('** Send error: {1}',),
        'kick': ('** Could not kick {1}: {2}',),
        'get': ('** Could not get {1}info for {ns}: {2}', False),
        'set': ('** Could not set {1}: {2}',),
        'kill': ('** Kill error: {1}',),
        'unknown': ('** Received unknown packet in {0}: {1}', False),
    }
    
    tablumps = Tablumps
    
    def __init__(self):
        self.tablumps = self.tablumps()
    
    def event_name(self, pkt):
        """ Determine the event name for a given packet. """
        namespace = pkt.cmd
        
        for conditions in self.names:
            
            if conditions[0] == namespace:
                subline = pkt.body.split('\n')[0]
                subline = subline.split(' ')
                
                if not subline or not subline[0]:
                    break
                
                namespace = '_'.join([namespace, subline[0]])
                
                if len(conditions) > 1 and len(subline) > 1:
                    if conditions[1] == subline[0]:
                        namespace = '_'.join([namespace, subline[1]])
                
                break
        
        return namespace if namespace in self.maps else 'unknown'
    
    def mapper(self, pkt):
        """ Map packets to a usable data structure.
            
            Return data mapped according to the conditions defined in
            the ``maps`` attribute.
        """
        pevent = PacketEvent(self.event_name(pkt))
        map = self.maps[pevent.name]
        return getattr(self, 'gen_'+pkt.cmd, self.sort)(pevent, pkt, map)
        
    def sort(self, pevent, data, map):
        """ Sort data according to the conditions in the given map. """
        for i, cond in enumerate(map):
            if not cond:
                continue
            
            if i in [0, 2]:
                # Handle mapping rules for pkt.param and the packet body
                ptab = cond[0] == '*'
                
                if ptab:
                    cond = cond[1:]
                
                val = data.param if i == 0 else data.body
                val = (val if not ptab else self.tablumps.parse(val)) if val else ''
                pevent.arguments[cond] = val
            
            if i is 1:
                # Handle mapping rules for packet arguments
                for item in cond:
                    if not item:
                        continue
                    
                    argn, name = item if isinstance(item, tuple) else (item, item)
                    ptab = argn[0] == '*'
                    
                    if ptab and argn == name:
                        name = argn[1:]
                    
                    val = '' if not argn in data.args.keys() else data.args[argn]
                    
                    if ptab:
                        val = self.tablumps.parse(val)
                    
                    pevent.arguments[name] = val
            
            if i is 3:
                # Rules for the sub packet, if there is any
                store = self.sort(store, Packet(data.body), cond)
            
            if i is 4:
                # Rule for storing the raw packet
                val = data.raw if data.raw else ''
                pevent.arguments[cond] = val
        
        return pevent
    
    def logger(self, event, ns, pkt):
        """ Return a log_list (message, channel[, bool(showns)[, bool(mute)]]).
            
            The message returned is based on the templates defined in the
            ``messages`` attribute of this class.
        """
        sequence = ['', ns, True, False, pkt]
        
        # Return None if we don't have a message for this packet.
        if not event.name in self.messages.keys():
            return None
        
        # Use custom log method if available.
        if hasattr(self, 'log_'+event.name):
            return getattr(self, 'log_'+event.name)(event, ns, pkt)
        
        # Reference message options.
        options = self.messages[event.name]
        
        if options is None or len(options) == 0:
            return None
        
        # Format the associated message.
        data = event.arguments.values()
        msg = (options[0].replace('{ns}', ns)).format(*data)
        
        # Trim any empty brackets.
        if msg[-3:] == ' []':
            msg = msg[:-3]
        
        # Store the message
        sequence[0] = msg
        options = [] if len(options) == 1 else options[1:]
        
        i = 2
        # Store any other options.
        for item in options:
            sequence[i] = item
            i+=  1
        
        return sequence
    
    def gen_recv(self, pevent, data, map):
        # Generic recv packet mapping operations.
        pevent.arguments['ns'] = data.param
        pevent = self.sort(pevent, Packet(data.body), map)
        
        if pevent.name in ('recv_msg', 'recv_action'):
            pevent.arguments['raw'] = data.raw
        
        return pevent

# EOF
