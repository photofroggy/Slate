''' dAmnViper.dA.oauth module
    Copyright (c) 2011, Henry "photofroggy" Rapley.
    Released under the ISC License.
    
    This module provides objects which can be used to authorize applications
    with deviantart.com's oAuth API. Note that this product is in no way
    affiliated with or endorsed by deviantART.com. This is not an official
    service of deviantART.com. This is an independent project created by
    photofroggy.
'''

from urllib import urlencode

from twisted.web import server
from twisted.web import resource
from twisted.internet import defer


class oAuthClient(object):
    """ oAuth client object.
        
        Technically, this object acts as a web server. The server listens for
        connections on localhost, and processes requests received.
        
        Deviantart uses an oAuth API to authorize third party applications.
        This is done by redirecting the user's web browser to a url provided
        by the application when requesting authorization.
        
        This server listens for the request given by the user's web browser (as
        a result of the redirect), processes the given data, gives a response
        to the browser, and provides the application with the request data.
        
        Any HTML or string given in the ``html`` argument is used as the
        response given to the user's web browser. The default HTML page is a
        simple page informing the user that they can close their web browser
        and return to the application. It is advised that you provide custom
        HTML to make the response match the design of your application, or just
        so that your application is mentioned in the response.
    """
    
    def __init__(self, _reactor, port=8080, resource=None, html=None):
        # Store input
        self._reactor = _reactor
        self.d = None
        self.port = port
        self.resource = resource
        self.html = html
        
        if self.resource is None:
            self.resource = AuthResource
        
        if self.html is None:
            self.html = html_response
        
        self.resource = self.resource(self.gotResponse, self.html)
    
    def serve(self):
        """ Start serving responses to localhost.
            
            This method returns a `Deferred` object. Add a callback to this
            deferred to perform an action when deviantART redirects the user's
            browser to `localhost`. Doing this, you should be able to retrieve
            authorization code. For example::
                
                def handle_auth(response):
                    try:
                        print 'Auth code:', response.args['code'][0]
                    except KeyError:
                        print 'Auth failed'
                    reactor.stop()
                
                client = oAuthClient(reactor, port, resource, html)
                # Start serving requests.
                d = client.serve()
                # Defer the handling or whatever.
                d.addCallback(handle_auth)
                
                reactor.run()
            
        """
        self.d = defer.Deferred()
        site = server.Site(self.resource)
        self.sitePort = self._reactor.listenTCP(self.port, site)
        return self.d
    
    def gotResponse(self, request):
        """ Defer processing the response. """
        request.notifyFinish().addCallback(self.deferred, request)
    
    def deferred(self, obj, request):
        """ Once again we delay processing of the response from dA. """
        self.sitePort.stopListening()
        self._reactor.callLater(1, self.d.callback, request)
        self.d = None


class AuthResource(resource.Resource):
    """ Authorize resource.
        
        This is the object which processes requests sent to localhost.
        Required for processing the response from deviantART when
        requesting an authorization code.
        
        This class is used by the ``oAuthClient`` object.
    """
    
    isLeaf=True
    
    def __init__(self, callback, html=None):
        self.callback = callback
        self.html = html
        
        if self.html is None:
            self.html = html_response
    
    def render_GET(self, request):
        """ Determine whether or not to pass the request to the application. """
        if 'favicon' in request.path:
            return ''
        
        data = request.args or None
        
        if data is None:
            return ''
        
        try:
            self.callback(request)
        except Exception as e:
            pass
        
        return self.html


html_response="""<!DOCTYPE html>
<html lang="en">
    <head>
        <meta charset=utf-8 />
        <title>Response Received!</title>
        <style>
            html, body {
                font-family: Verdana, Arial, sans-serif;
                line-height: 1.6em;
                font-size: small;
            }
            
            body {
                width: 800px;
                margin: 5em auto 5em auto;
                background-color: #c6dbe0;
                color: #157171;
            }
            
            div {
                background-color: #FFFFFF;
                border: 1px solid #69aab8;
                padding: 2em 5em;
                -moz-border-radius: 3em;
                -webkit-border-radius: 3em;
                -moz-box-shadow: 2px 2px 3px #003333;
                -webkit-box-shadow: 2px 2px 3px #003333;
                box-shadow: 2px 2px 3px #003333;
            }
            
            h1 {
                font-family: Georgia, "Palatino Linotype", Palatino, "Book Antiqua", "Times New Roman", Times, serif;
                padding-bottom: .5em;
                color: #168787;
                font-size: 26pt;
            }
            
            p {
                margin: 5em
                padding-right: 10em;
                padding-left: 2em;
            }
            
            em {
                color: #003333;
                font-style: normal;
                font-weight: bold;
            }
            
            @media print {
                section { border: none; }
                h1 {
                    margin: .5em 0em 0em 0em;
                    padding: 2px 50px 10px 10px;
                    border-bottom: 3px solid #000000;
                    color: #003333;
                    font-size: 32pt;
                }
            }
        </style>
    </head>
    <body>
        <div>
            <h1>Response received!</h1>
            <p>
                The application has now received your response. You can <em>
                close this browser window</em> and return to your application.
                Easy as pie.
            </p>
        </div>
    </body>
</html>
"""


# EOF
