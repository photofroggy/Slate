''' Command data
    Provides a binding object and an event object.
'''


from functools import wraps

from reflex import data


class Binding(data.Binding):
    """Command Binding class."""
    
    def __init__(self, method, options):
        super(Binding, self).__init__(method, 'command', options)
        
        cmd = self.options['cmd'] if isinstance(self.options['cmd'], str) else self.options['cmd'][0]
        
        if ' ' in cmd:
            raise ValueError
        
        self.type = '<event[\'command:{0}\'].binding>'.format(cmd)
        
        self.group = 'Guests'
        self.level = 25
    
    def set_privs(self, groups):
        grp = self.group
        
        if len(self.options) > 1:
            grp = self.options.get('priv', self.group)
            if grp != self.group:
                grp = groups.find(grp, True)
                if grp is None:
                    grp = self.group
        
        self.group = grp
        self.level = groups.find(grp)



def arguments(data=False, start=0, finish=False, separator=' ', sequence=False):
    """ This method extracts specific arguments from a message. """
    if data == '':
        return '' if not sequence else ['']
    
    data = data.split(separator)
    
    if len(data) <= start:
        return '' if not sequence else ['']
    if isinstance(finish, bool) or finish == None:
        data = data[start:] if finish else [data[start]]
    else:
        data = data[start:] if len(data) <= finish else data[start:finish]
    return data if sequence else separator.join(data)


class Command(data.Event):
    """Command event class."""
    
    def init(self, event, data):
        self.arguments = self._args_wrapper()
        
    def __str__(self):
        return '<event[\'command:'+self.trigger+'\']>'
    
    def _args_wrapper(self):
        @wraps(arguments)
        def wrapper(start=0, finish=False, separator=' ', sequence=False):
            return arguments(self.message, start, finish, separator, sequence)
        return wrapper


# EOF
