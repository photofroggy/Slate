''' Reflex data objects.
    Copyright (c) 2011, Henry "photofroggy" Rapley.
    Released under the ISC License.
    
    This module contains data objects used in Reflex!
    Mainly just the Binding and Event classes!
'''

class Binding(object):
    """ Event binding.
    
        Each instance represents a different binding. A binding stores
        information showing how a certain method is related to a certain
        event. Different attributes define the conditions for the
        relationship. The attributes are as follows:
        
        * *callable* **call** - The method used to handle the specified
          event.
        * *str* **event** - The name of the event that the method
          defined in ``call`` is used to handle.
        * *dict* **optoins** - This dict defines a set of items that,
          when defined, must match the respective items provided when
          the event defined by ``event`` is triggered. If the items do
          not match, then the handler is not used. Different Rulesets
          can modify this behaviour.
        * *str* **type** - A string representation of the binding.
        
        The constructor of this class takes the above fields as input,
        apart from ``type``.
    """
    
    call = None
    event = None
    options = {}
    type = None
    
    def __init__(self, method, event, options):
        """All the given values are stored on instantiation of an event binding."""
        self.call = method
        self.event = event
        self.options = options
        self.type = '<event[\''+event+'\'].binding>'
        self.init()
        
    def init(self):
        """Overwrite this method when doing stuff on instantiation."""
        pass

class Event(object):
    """ Event class.
        
        Instances of this class are used to represent events, and store
        information specific to the event being represented. The
        constructor takes the following input:
        
        * *str* **event** - The name of the event that the object
          represents.
        * *list* **data** - The data relating to the event being
          represented by the object.
        
        The event name is stored under the attribute ``name``. The
        ``data`` parameter should be a list of pairs, defining a key and
        a value each. The object stores these ``(key, value)`` pairs as
        ``obj.<key> = <value>``.
    """
    
    def __init__(self, event, data=[]):
        self.name = event
        self.rules = []
        for key, value in data:
            if key.lower() in ['rules', 'name']:
                continue
            setattr(self, key, value)
            self.rules.append(value)
        self.init(event, data)
    
    def init(self, event, data):
        """Overwrite this method if you need to do stuff on instatiation. Do not overwrite __init__."""
        pass
    
    def __str__(self):
        return '<event[\'' + self.name + '\']>'
    
# EOF
