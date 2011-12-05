''' dAmnViper.data module
    Copyright (c) 2011, Henry "photofroggy" Rapley.
    Released under the ISC License.
    
    This module provides the Channel object, which represents a
    joined channel. The object stores information about the channel,
    such as the title/topic, and users in the channel.
'''

from dAmnViper.parse import Packet

class Channel(object):
    """ Objects representing dAmn channels.
    
        Information about the channels are stored in here. The different
        attributes of the object are as follows:
        
        * ``title`` - This is an instance of the class
          ``Channel.header``, and stores information about the title of
          the channel. The object has the attributes ``content``, ``by``
          and ``ts``. These store the content of the title, the person
          who set the title, and the timestamp from when they set it,
          respectively.
        * ``topic`` - Similar to the ``title`` attribute, but it stores
          information about the channel's topic, as opposed to the
          channel's title.
        * ``pc`` - Stores information about the channel's privclasses.
        * ``pc_order`` - A list storing the the privclass names in order
          of hierarchy. This is to allow applications to display
          information more easily if needed.
        * ``member`` - A dictionary storing information about each user
          currently in the channel.
        * ``namespace`` - The channel's full namespace. This is usually
          a string in the form ``chat:channel_name``. This can differ
          depending on the type of channel the object represents.
        * ``shorthand`` - The shorthand form of the channel
          ``namespace``. This is usually a string in the format
          ``#channel_name`` if the namespace is of the format
          ``chat:channel_name``. This can differ depending on the type
          of channel the object represents.
        * ``type`` - A string in for format ``<dAmn channel
          'namespace'>`` where ``namespace`` is the same as the object's
          ``namespace`` attribute.
        
        Calling ``str(channel)``, where ``channel`` is an instance of
        the ``Channel`` class, returns the ``namespace`` attribute.
        
        As an example, here is what some of the attributes would look
        like for the **#Botdom** channel when the object is created::
            
            >>> channel = Channel('chat:Botdom', '#Botdom')
            >>> channel.namespace
            'chat:Botdom'
            >>> channel.shorthand
            '#Botdom'
            >>> str(channel)
            'chat:Botdom'
        
        The other attributes would be empty objects of their respective
        types until the appropriate data is received from the server.
    """
    
    class Header:
        def __init__(self):
            self.content = ''
            self.by = ''
            self.ts = 0.0
    
    def __init__(self, namespace, shorthand):
        """Set up all our variables."""
        self.title = Channel.Header()
        self.topic = Channel.Header()
        self.pc = {}
        self.pc_order = []
        self.member = {}
        
        self.namespace = namespace
        self.shorthand = shorthand
        
        self.type = '<dAmn channel \''+self.namespace+'\'>'
    
    def process_property(self, data):
        """ Called when receive a property packet for the channel.
            
            This method makes sure that the data is stored in the right
            places in the object.
        """
        if data.arguments['p'] == 'title':
            self.title.content = data.arguments['value']
            self.title.by = data.arguments['by']
            self.title.ts = data.arguments['ts']
        
        if data.arguments['p'] == 'topic':
            self.topic.content = data.arguments['value']
            self.topic.by = data.arguments['by']
            self.topic.ts = data.arguments['ts']
        
        if data.arguments['p'] == 'privclasses':
            self.pc = Packet(data.arguments['value'], ':').args
            self.pc_order = sorted(self.pc.keys(), key=int)
            self.pc_order.reverse()
        
        if data.arguments['p'] == 'members':
            member = Packet(data.arguments['value'])
            while member.cmd != None and len(member.args) > 0:
                self.register_user(member)
                member = Packet(member.body)
    
    def register_user(self, info, user = None):
        """ Called when a user joins the channel.
            
            Simply store their information in the ``member`` dictionary.
        """
        user = user if user != None else info.param
        if user in self.member:
            self.member[user]['con']+= 1
        else:
            self.member[user] = info.args
            self.member[user]['con'] = 1
    
    def __str__(self):
        return self.namespace

# EOF
