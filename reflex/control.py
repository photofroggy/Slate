''' Events system for Python.
    Copyright (c) 2011, Henry "photofroggy" Rapley.
    Released under the ISC License.
    
    The idea of this was to keep things simple but still alow things to be
    quite powerful. Therefore I have introduced the idea of "event rules",
    where events can have a class assigned to them to handle bindings,
    unbindings, and triggers.
    
    Hopefully this will allow for a flexible and powerful module system.
'''

# Standard Lib imports.
import sys
import imp
import pkgutil
import inspect
import traceback
from functools import wraps
from collections import Callable

# Reflex imports
from reflex.data import Event
from reflex.data import Binding
from reflex.base import Ruleset


class EventManager(object):
    """ The EventManager class provides a simple way to manage
        events and their bindings. This is one of the main things
        that application developers should be interested in using.
        
        Using the EventManager class is simple. All you have to do
        is make an instance of the class, then create event bindings
        using the ``bind()`` method. Once you have done that, you can trigger
        events using the ``trigger()`` method. A simple example is below::
        
            from reflex.data import Event
            from reflex.control import EventManager
            
            events = EventManager()
            
            def example(event, *args):
                print('Hello, world')
            
            events.bind(example, 'test')
            
            events.trigger(Event('test'))
        
        The above example does not show the full power of the system. View
        the tutorials to get a better idea of how things can be used.
        
        Input Parameters:
        
        * *callable* **stdout** - A reference to the method being used to write
          output to the screen. If ``None`` is given, a simple method that
          prints the message with a newline is used.
        * *callable* **stddebug** - A reference to the method being used to
          write debug messages to the screen. If ``None`` is given, a do-nothing
          method is used.
        * **args** and **kwargs** - Additional arguments can be passed here. These
          arguments will be passed to the ``init()`` method. Child classes
          should override the ``init()`` method to make use of any extra
          parameters passed to the constructor.
    """
    
    class info:
        version = 1
        build = 14
        stamp = '11122011-032054'
        name = 'Charged'
        state = 'RC'
    
    def __init__(self, stdout=None, stddebug=None, *args, **kwargs):
        self._write = stdout or (lambda n: None)
        self.debug = stddebug or (lambda n: None)
        self._rules = Ruleset
        self.map = {}
        self.rules = {}
        self.init(*args, **kwargs)
        self.default_ruleset(*args)
    
    def init(self, *args, **kwargs):
        """ This method is called by ``__init__``.
            
            On its own, it doesn't do anything. This is designed as a
            method which can be overridden by child classes so developers
            don't have to interfere with ``__init__``.
            
            This method is given the same input given to ``__init__``.
        """
        pass
    
    def default_ruleset(self, *args):
        """ Revert rulesets to defaults.
            
            This method simply loads the default ruleset into the
            ``rules`` attribute. If any other rulesets were present,
            they will be lost.
        """
        self.rules = {'default': self._rules(args, self.map, self._write, self.debug)}
    
    def define_rules(self, event, ruleset, *args):
        """ Define a ruleset.
            
            Input parameters:
            
            * *str* **event** - The event that the ruleset defines the
              rules for.
            * *Ruleset* **ruleset** - The ruleset to use for the given
              ``event`` namespace. This should be a class! The method
              creates an instance of the class itself.
            * *args* - Any other arguments that might need to be given
              to the ruleset on instantiation.
            
            This method is used to define a ruleset for a given event
            namespace.
        """
        if not issubclass(ruleset, Ruleset):
            return False
        self.rules[event] = ruleset(args, self.map, self._write, self.debug)
        return True
    
    def bind(self, method, event, **options):
        """ Bind a method to an event.
            
            Input parameters:
            
            * *callable* **method** - This is a method that will be
              invoked when the event defined in the event parameter is
              triggered.
            * *str* **event** - The event that the method is being bound
              to.
            * *list* **options** - An iterable of conditions the event
              must meet. If given, then corresponding items provided
              when the event is triggered must match these items.
            * *list* **additional** - Any additional arguments which
              developers may want to use in their systems.
            
            This is essentially the same concept as creating an event
            listener. The binding is actually done in the ruleset object
            being used for the event.
            
            If the event has no explicit ruleset, then the default
            ruleset is used (reflex.base.Ruleset).
            
            Returns ``None`` on failure. Otherwise, returns the binding
            created. The event binding is an instance of the
            ``refelx.data.Binding`` class.
        """
        if not isinstance(method, Callable):
            return None
        ruleset = self.rules.get(event, self.rules['default'])
        return ruleset.bind(method, event, **options)
    
    def unbind(self, method, event, **options):
        """ Remove an event binding for a method.
            
            This is the reverse of the bind method. Once again, the
            unbinding is actually done by the ruleset object being used
            for the event.
        """
        ruleset = self.rules.get(event, self.rules['default'])
        return ruleset.unbind(method, event, **options)
    
    def handler(self, event, **options):
        """ Create an event handler.
            
            This method provides a decorator interface for the ``bind()``
            method. A brief example is given below::
            
                from reflex.data import Event
                from reflex.control import EventManager
                
                events = EventManager()
                
                # Create an event handler using the decorator method.
                
                @events.handler('example')
                def my_handler(data, *args):
                    print('Hello, world!')
                
                # Trigger the 'example' event.
                events.trigger(Event('example'))
                # >>> Hello, world!
        """
        def decorate(func):
            if not isinstance(func, Callable):
                return func
            func.binding = self.bind(func, event, **options)
            return func
        return decorate
    
    def trigger(self, data=None, *args):
        """ Trigger an event.
            
            Input parameters:
            
            * ``reflex.data.Event`` **data** - This parameter should be
              an event object, using either the ``reflex.data.Event``
              class or a subclass of it.
            * **args** - Any other additional arguments that developers
              want to pass to event handlers.
            
            This method is mainly a wrapper for the ``run()`` method of
            the ruleset object being used for the event defined by the
            object given in the ``data`` parameter.
        """
        if not hasattr(data, 'name') or not hasattr(data, 'rules'):
            return []
        event = data.name
        
        if not event in self.map.keys():
            return []
        
        ruleset = self.rules.get(event, self.rules['default'])
        
        if hasattr(ruleset, 'trigger'):
            return ruleset.trigger(data, *args)
        
        return [ruleset.run(binding, data, *args) for binding in self.map[event]]
    
    def clear_bindings(self):
        """ This method removes all event bindings that are being stored
            in the event manager.
        """
        self.map = {}
        for rule in self.rules:
            self.rules[rule].set_map(self.map)
    
    def bindset(self, source):
        """ Returns a bindset.
            
            Input parameters:
            
            * *str* **source** - The binding source to be used when binding or
              unbinding events.
            
            This method is only meant for use in
            ``reflex.base.reactor``. This method returns a tuple
            containing both the ``bind()`` and ``unbind()`` methods,
            except that the methods have been wrapped to always use the
            same ``source`` parameter, as given to this method.
            
            **Note:** This method is currently not in use, so may be
            removed.
        """
        def wrapit(func):
            @wraps(func)
            def new(*args, **kwargs):
                return func(source, *args, **kwargs)
            return new
        return (wrapit(self.bind), wrapit(self.unbind))


class PackageBattery(object):
    """ The Package Battery is the base class that provides
        the functionality of loading all modules within a given
        package, and according to certain conditions.
        
        This functionality is used by the ``ReactorBattery`` and the
        ``RulesetBattery`` in Reflex.
        
        Input Parameters:
        
        * *callable* **stdout** - Reference to a method that displays output on
          screen. This should be a method which displays normal messages that
          this object tries to display on-screen. By default this is a method
          which simply writes the output to stdout with a newline appended.
        * *callable* **stddebug** - Similar to ``stdout``, this is a method used
          by the object to display output, but this method is used to display
          debug messages, so the method provided should only actually show the
          messages given to it when the application is running in debug mode. By
          default this is a do-nothing lambda.
        
    """

    def __init__(self, stdout=None, stddebug=None, *args, **kwargs):
        self.log = stdout or (lambda n: None)
        self.debug = stddebug or (lambda n: None)
        self.modules = {}
        self.loaded = {}
        self.init(*args, **kwargs)
    
    def init(self, *args, **kwargs):
        """ This is a do-nothing method.
            
            If you are extending this class and want to perform operations when
            an instance of the class is made, override this method. This method
            is called by ``__init__()``.
        """
        pass
    
    def load_modules(self, package, required='ClassName'):
        self.debug('** Checking modules in the {0} package.'.format(package.__name__))
        modules = {}
        walker = pkgutil.walk_packages(package.__path__, package.__name__ + '.')
        for tup in walker:
            name = tup[1]
            
            self.debug('** Found module \'{0}\'.'.format(name))
                
            if name in self.modules.keys():
                self.debug('** Previously loaded module. Reloading!')
                imp.reload(self.modules[name])
                modules[name] = self.modules[name]
                continue
                
            loader = pkgutil.find_loader(name)
            mod = loader.load_module(name)
            
            if not hasattr(mod, required):
                self.debug('>> Ignoring module {0}.'.format(name))
                self.debug('>> Module contains no {0} class.'.format(required))
                continue
            
            modules[name] = mod
        self.modules = modules
    
    def load_objects(self, manager, package, cls='ClassName', *args, **kwargs):
        """ Loads all objects from a given package.
            
            Input parameters:
            
            * :ref:`reflex.control.EventManager <eventmanager>` **manager** -
              A reference to an EventManager object.
            * *package* **package** - The package from which to load modules and
              their objects, depending on if they have any.
            * *str* **cls** - The name of the class to look for in each module
              within the package defined in ``package``.
            
            Any extra arguments are passed to the Reactor classes on
            instantiation.
            
        """
        if self.modules == {}:
            self.log('** Loading {0}s...'.format(cls.lower()))
        self.load_modules(package, cls)
        self.loaded = {}
        for name, mod in self.modules.items():
            try:
                self.load_object(manager, mod, cls, *args, **kwargs)
            except Exception as e:
                self.log('>> Failed to load {0} from {1}!'.format(cls.lower(), name))
                self.log('>> Error:')
                tb = traceback.format_exc().splitlines()
                for line in tb:
                    self.log('>> {0}'.format(line))
        
        self.debug('** Loaded {0}s: {1}'.format(cls.lower(), ', '.join(self.loaded.keys())))
        
    def load_object(self, manager, module, cls, *args, **kwargs):
        """ Load a single object from a single class. """
        obj = getattr(module, cls)(*args, **kwargs)
        name = str(obj.__class__).split('.')[-2].replace('_', ' ')
        self.loaded[name] = obj
    
        
class ReactorBattery(PackageBattery):
    """ The Reactor Battery provides a simple way to load
        all rectors stored inside a given package. 
    
        This can be used as the basis for an extension system in an application,
        if implemented properly. To use the class, create an instance of the
        class, and call the load_reactors module with appropriate parameters.
        For example, if your application's plugin package was called ``plugins``
        and the plugin classes were called ``Plugin`` in each module, you would
        do something similar to the following to load the plugins::
        
            import plugins
            from reflex.control import EventManager
            from reflex.control import ReactorBattery
            
            # Create an event manager.
            events = EventManager()
            
            # Create a battery.
            battery = ReactorBattery()
            # Load our plugins.
            battery.load_objects(events, plugins, 'Plugin',)
            
            # Plugins can now be accessed as such:
            #   battery.loaded[plugin_name]
            # Easy as pie!
        
        Quite simple, really. It takes more than that to fully implement an
        extension or plugin system, but the above provides a solid base for any
        system you can think up. Or it could be terrible.
    """
    
    def load_modules(self, package, required='Reactor'):
        super(ReactorBattery, self).load_modules(package, required)
    
    def load_objects(self, manager, package, cls='Reactor', *args, **kwargs):
        """ Loads all reactors from a given package.
            
            Input parameters:
            
            * *:ref:`reflex.control.EventManager <eventmanager>`* **manager** -
              A reference to an EventManager object. Reactors are given this
              reference so that they can create event bindings.
            * *package* **package** - The package from which to load modules and
              their Reactor classes, depending on if they have any.
            * *str* **cls** - The name of the class to look for in each module
              within the package defined in ``package``.
            
            Any extra arguments are passed to the Reactor classes on
            instantiation.
            
        """
        super(ReactorBattery, self).load_objects(manager, package, cls, *args, **kwargs)
    
    def load_object(self, manager, module, cls, *args, **kwargs):
        robj = getattr(module, cls)(manager, *args, **kwargs)
        rname = robj.name
        self.loaded[rname] = robj
    
        
class RulesetBattery(PackageBattery):
    """ The Ruleset Battery provides a simple way to load
        all rulesets stored inside a given package. 
    
        Use this in conjunction with the ReactorBattery to create a richer
        plugin system. Rulesets allow greater control over how your system
        handles specific events. Below is a simple example of how to use the
        Ruleset Battery::
        
            import plugins
            import rules
            from reflex.control import EventManager
            from reflex.control import ReactorBattery
            from reflex.control import RulesetBattery
            
            # Create an event manager.
            events = EventManager()
            
            # Create a ruleset battery.
            rulesets = RulesetBattery()
            # Load our rulesets.
            rulesets.load_objects(events, rules)
            # All rulesets in the rules package should now be loaded
            # and registered with the event manager.
            
            # Create a reactor battery.
            plugin = ReactorBattery()
            # Load our plugins.
            plugin.load_objects(events, plugins, 'Plugin')
            
            # Plugins can now be accessed as such:
            #   plugin.loaded[plugin_name]
            # Easy as pie!
        
        There. An easy way to make your plugin system more flexible!
    """
    
    def load_modules(self, package, required='Ruleset'):
        super(RulesetBattery, self).load_modules(package, required)
    
    def load_objects(self, manager, package, cls='Ruleset', *args, **kwargs):
        """ Loads all rulesets from a given package.
            
            Input parameters:
            
            * :ref:`reflex.control.EventManager <eventmanager>` **manager** -
              A reference to an EventManager object. This is used to define
              rules using the rulesets in the given package.
            * *package* **package** - The package from which to load modules and
              their Ruleset classes, depending on if they have any.
            * *str* **cls** - The name of the class to look for in each module
              within the package defined in ``package``.
            
            Any extra arguments are passed to the Ruleset classes on
            instantiation.
            
        """
        super(RulesetBattery, self).load_objects(manager, package, cls, *args, **kwargs)
    
    def load_object(self, manager, module, cls, *args, **kwargs):
        rulename = str(module.__name__).split('.')[-1]
        manager.define_rules(rulename, getattr(module, cls), *args)
        self.loaded[rulename] = 1

# EOF
