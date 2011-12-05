''' dAmnViper.net module
    Copyright (c) 2011, Henry "photofroggy" Rapley.
    Released under the ISC License.
    
    This module provides classes used to actually connect to dAmn using
    Twisted. The ConnectionFactory starts connections and handles disconnects.
    The IOProtocol handles basic IO operations on the connection, but delegates
    most of the processing to an instance of the Client class from the
    dAmnViper.base module.
'''

# Standard library
import time

# Twisted library imports
from twisted.internet import reactor
from twisted.internet.protocol import Protocol
from twisted.internet.protocol import ClientFactory

# Viper stuff
from dAmnViper.parse import Packet


class ConnectionFactory(ClientFactory):
    """ Connection management.
        
        Instances of this class are used by the base :py:class:`ChatClient
        class <dAmnViper.base.ChatClient>` to connect to chat networks.
        
        The object returns instances of :py:class:`ChatProtocol
        <dAmnViper.net.ChatProtocol>` when a connection is made and
        handles disconnects and connection failures.
        
        This object should not be used directly by applications using
        dAmnViper.
    """
    
    stdout = None
    debug = None
    client = None

    def __init__(self, client, stdout=None, debug=None):
        """Initialise up in this motherfucka"""
        self.log = stdout
        self.debug = debug
        self.client = client
        
        if self.log is None:
            self.log = lambda m: None
        if self.debug is None:
            self.debug = lambda m: None
    
    def startedConnecting(self, connector):
        """ Called by twisted when we start to connect. """
        self.client.startedConnecting(connector)
    
    def create_protocol(self):
        return ChatProtocol(self, self.client, self.stdout, self.debug)
        
    def buildProtocol(self, addr):
        """ Called by twisted when a protocol is needed.
            
            Twisted calls this method when a connection can be
            established with the server. This method creates an instance
            of the :py:class:`ChatProtocol <dAmnViper.net.ChatProtocol>`
            class. This instance is given to the :py:class:`ChatClient
            <dAmnViper.base.ChatClient>` object that the factory belongs
            to, and returned to twisted.
        """
        protocol = self.create_protocol()
        self.client.set_protocol(protocol)
        return protocol
    
    def clientConnectionLost(self, connector, reason):
        """ Called by twisted when a connection is lost.
            
            Displays a message notifying the connection loss and tells
            the :py:class:`ChatClient <dAmnViper.base.ChatClient>` object that
            there is no longer a connection open.
        """
        
        self.client.connectionLost(connector, reason)
    
    def clientConnectionFailed(self, connector, reason):
        """ Called by twisted when we fail to connect properly.
            
            The behaviour of this method is similar to the
            ``clientConnectionLost`` method.
        """
        
        self.client.connectionFailed(connector, reason)


class ChatProtocol(Protocol):
    """ Protocol layer for the dAmn connection.
        
        Instances of this class are used to directly communicate with
        the connection to dAmn via twisted, and gives any data received
        to the :py:class:`ChatClient <dAmnViper.base.ChatClient>` instance
        being used for this connection.
        
        This object should not be used directly by applications using
        dAmnViper.
    """
    
    conn = None
    client = None
    log = None
    debug = None
    __buffer = None
    
    def __init__(self, conn, client, stdout=None, debug=None):
        """ Initialise the protocol. """
        # Store our objects
        self.conn = conn
        self.client = client
        self.log = stdout
        self.debug = debug
        self.__buffer = ''
        
        # Make sure we have callables for logging stuff.
        if self.log is None:
            self.log = lambda m: None
        
        if self.debug is None:
            self.debug = lambda m: None
    
    def connectionMade(self):
        """ Called by twisted when we have connected.
            
            This method simply calls the same method in the client object.
        """
        self.client.connectionMade()
    
    def dataReceived(self, data):
        """ Called by twisted when data is received.
            
            The data received is added to out buffer. If there are any full
            packets in the buffer, these packets are sent to the
            :py:class:`ChatClient <dAmnViper.base.ChatClient>` instance to be
            parsed properly.
            
            Any event handling relating to specific packets is done in the
            ``ChatClient`` instance.
        """
        
        # Tell the client some data has arrived. Woo...
        self.client.dataReceived(data)
        
        # Split on null.
        self.__buffer+= data
        raw = self.__buffer.split('\0')
        self.__buffer = raw.pop()
        
        for chunk in raw:
            packet = Packet(chunk)
            
            # If it's a ping packet, send a pong straight away!
            if packet.cmd == 'ping':
                self.send_packet('pong\n')
            
            # Let the client do whatever it needs to with the packet.
            self.client.handle_pkt(packet, time.time())
    
    def send_packet(self, data):
        """ A wrapper function for sending packets to the server.
            
            Here, a null character (``\\0``) is appended to the given
            data, and we return the number of characters we have tried
            send to the server.
        """
        data = '{0}\0'.format(data)
        self.transport.write(data)
        return len(data)


# EOF
