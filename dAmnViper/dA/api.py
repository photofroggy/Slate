''' dAmnViper.dA.oauth module
    Copyright (c) 2011, Henry "photofroggy" Rapley.
    Released under the ISC License.
    
    This module provides objects which can be used to authorize applications
    with deviantart.com's oAuth API. Note that this product is in no way
    affiliated with or endorsed by deviantART.com. This is not an official
    service of deviantART.com. This is an independent project created by
    photofroggy.
'''


import json
from urllib import urlencode

from twisted.web import server
from twisted.web import resource
from twisted.internet import defer
from twisted.internet import protocol
from twisted.web.client import Agent
from twisted.web.http_headers import Headers


from dAmnViper.dA.oauth import oAuthClient


class ResponseReceiver(protocol.Protocol):
    """ Response receiver.
        
        A simple object used to receive responses from a web request.
    """
    
    def __init__(self, deferred):
        self.d = deferred
        self.b = ''
    
    def dataReceived(self, data):
        """ Store any received data in the buffer. """
        self.b+= data
    
    def connectionLost(self, reason):
        """ Make sure we do something with the response. """
        self.d.callback(self.b)


class Response(object):
    """ API Response object. Stores response data. """
    
    def __init__(self, head, data):
        self.head = head
        self.raw_data = data
        
        try:
            self.data = json.loads(str(data))
        except Exception as e:
            self.data = None


class Request(object):
    """ Send an API request.
        
        This is a helper object to send requests to API methods.
        
        A deferred method must be provided, as this object will call the
        deferred with the response from the api request.
    """
    
    def __init__(self, _reactor, deferred, url, agent='dAmnViper/dA/api/request', response=None):
        self._reactor = _reactor
        self.d = deferred
        self.agent = agent
        self.url = url
        self.agent = agent
        self.response_obj = response
        
        if self.response_obj is None:
            self.response_obj = Response
        
        self.start_request()
    
    def start_request(self):
        """ Send the api request to deviantART. """
        agent = Agent(self._reactor)
        d = agent.request('POST', self.url, Headers({'User-Agent': [self.agent]}), None)
        d.addCallback(self.received_response)
    
    def received_response(self, response):
        """ Received a response. Get the response body. """
        self.response = response
        d = defer.Deferred()
        d.addCallback(self.got_data)
        response.deliverBody(ResponseReceiver(d))
    
    def got_data(self, data):
        """ Received when we have the response body. """
        self.d.callback(self.response_obj(self.response, data))


class APIClient(object):
    """ Client for deviantart.com's API.
        
        This client acts as a client which can be used to interact with
        deviantART.com's API. The client object provides methods to aid in
        authorizing applications, and for interacting with the ``user`` api
        methods.
        
        You can use the ``call`` method to perform api calls for any methods
        provided by deviantART.com. Documentation of the API can be found
        at this web page: http://www.deviantart.com/developers/
        
        Using the ``url`` method directly allows you to generate your urls
        for api calls. The ``call`` method uses this internally in combination
        with the ``sendRequest`` method.
        
        If all you need to do is authorize your application, then it may be
        best to only use the objects provided in the ``dA.oauth`` module in
        this package.
    """
    
    def __init__(self, _reactor, client_id, client_secret, auth_code=None, token=None, refresh_token=None, agent='dAmnViper/dA/api/apiclient', api_url=None):
        self._reactor = _reactor
        self.client_id = client_id
        self.client_secret = client_secret
        self.auth_code = auth_code
        self.token = token
        self.refresh_token = refresh_token
        self.agent = agent
        # URL stuff
        self.draft = 'draft15'
        self.api_url = api_url or 'https://www.deviantart.com/'
        # Custom? Maybe
        self.init()
    
    def init(self):
        """ Override this method if you want to customise the class a bit. """
        pass
    
    def auth_app(self, port=8080, resource=None, html=None):
        """ Start the oAuth client.
            
            Provide custom HTML in the ``html`` parameter to provide a custom
            response page to be given in return to web requests.
        """
        client = oAuthClient(self._reactor, port, resource, html)
        # Start serving requests.
        d = client.serve()
        # Defer the handling or whatever.
        d.addCallback(self._authResponse)
        return d
    
    def _authResponse(self, response):
        """ Process oAuth responses. """
        if 'error' in response.args:
            return {'status': False, 'data': response}
            
        if 'code' in response.args and response.args['code'][0]:
            self.auth_code = response.args['code'][0]
            return {'status': True, 'data': response}
        
        return {'status': False, 'data': response}
    
    def url(self, klass, method=None, api='api', **kwargs):
        """ Create an API URL based on the input.
            
            Typically, the format for api urls is as follows::
                
                "https://www.deviantart.com/api/draft15/class/method?arg=value"
            
            The ``klass`` and ``method`` parameters are used for the class and
            method values in the url. Method names are not required, but appear
            more often than not in the api.
        """
        args = {}
        
        for key, value in kwargs.iteritems():
            if not value:
                continue
            args[key] = value
        
        return '{0}{1}/{2}/{3}{4}{5}'.format(self.api_url, api, self.draft, klass,
            '' if method is None else '/{0}'.format(method),
            '' if not args else '?{0}'.format(urlencode(args)))
    
    def requiresToken(self, refresh=False):
        """ If the token is not set, raise a ``ValueError``. """
        if self.token is None or (refresh and self.refresh_token is None):
            raise ValueError('token required for this method')
    
    def sendRequest(self, url, response_obj=None):
        """ Send a request to the api.
            
            Returns a ``Deferred`` object.
        """
        d = defer.Deferred()
        Request(self._reactor, d, url, self.agent, response_obj)
        return d
    
    def call(self, klass, method=None, api='api', **kwargs):
        """ Call an api method.
            
            This method is a shortcut for combining both ``.sendRequest`` and
            ``.url``.
        """
        return self.sendRequest(self.url(klass, method, api, **kwargs))
    
    def grant(self, auth_code=None, req_state=None):
        """ Request a grant token. """
        if auth_code != None:
            self.auth_code = auth_code
        
        if self.auth_code is None:
            raise ValueError('Authorization code must not be None')
        
        d = self.sendRequest(self.url('token', api='oauth2',
            client_id=self.client_id,
            client_secret=self.client_secret,
            grant_type='authorization_code',
            state=req_state,
            code=self.auth_code
        ))
        d.addCallback(self.handle_grant)
        
        return d
    
    def refresh(self, refresh_token=None, req_state=None):
        """ Request a new grant token using a refresh token. """
        self.refresh_toke = refresh_token or self.refresh_token
        
        self.requiresToken(True)
        
        d = self.sendRequest(self.url('token', api='oauth2',
            client_id=self.client_id,
            client_secret=self.client_secret,
            grant_type='refresh_token',
            state=req_state,
            refresh_token=self.refresh_token
        ))
        
        d.addCallback(self.handle_grant)
        return d
    
    def handle_grant(self, response):
        """ Handle the response to the grant api call. """
        if response.data is not None and response.data['status'] == 'success':
            self.token = response.data['access_token']
            self.refresh_token = response.data['refresh_token']
            return {'status': True, 'data': response}
        
        return {'status': False, 'data': response}
    
    def placebo(self, token=None):
        """ Check that the access token is still valid. """
        if token != None:
            self.token = token
        else:
            self.requiresToken()
        
        return self.sendRequest(self.url('placebo', access_token=self.token))
    
    def user_whoami(self, token=None):
        """ Request info on the user. """
        if token != None:
            self.token = token
        else:
            self.requiresToken()
        
        return self.sendRequest(self.url('user', 'whoami', access_token=self.token))
    
    def user_damntoken(self, token=None):
        """ Request the user's dAmn authtoken. """
        if token != None:
            self.token = token
        else:
            self.requiresToken()
        
        return self.sendRequest(self.url('user', 'damntoken', access_token=self.token))


# EOF
