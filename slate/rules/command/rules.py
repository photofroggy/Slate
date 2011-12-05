''' Command rules.
'''

import traceback

from reflex import base

from slate.rules.command import data

class Ruleset(base.Ruleset):
    
    def init(self):
        self.index = {}
    
    def bind(self, meth, event, **options):
        """ Creates a command binding.
            
            This method attempts to create a command binding for the given
            method. If successful, this method returns the command binding.
            On failure, ``None`` is returned.
        """
        if not options:
            return None
        
        if not options['cmd']:
            return None
        
        if not 'command' in self.mapref:
            self.mapref['command'] = []
        
        # Check if the command binding already exists.
        for binding in self.mapref['command']:
            if (binding.call, binding.options) is (meth, options):
                return None
        
        try:
            cmd = options['cmd'].lower()
            if ' ' in cmd:
                raise AttributeError
        except AttributeError as e:
            self.debug('>> Command name \'{0}\' is invalid'.format(cmd))
            return None
        
        if cmd in self.index:
            self.debug('>> Command \'{0}\' already exists'.format(cmd))
            return None
        
        binding = data.Binding(meth, options)
        # binding.set_privs(self.user.groups)
        self.mapref['command'].append(binding)
        self.index[cmd.lower()] = len(self.mapref['command']) - 1
        
        return binding
        
    
    def unbind(self, meth, event, **options):
        """ Remove a command binding.
            
            This method attempts to remove a command binding for the given
            method. If successful, ``True`` is returned. On failure, ``False``
            is returned.
        """
        if not options:
            return False
        
        try:
            cmd = options['cmd'].lower()
            if ' ' in cmd:
                raise AttributeError
        except AttributeError as e:
            self.debug('>> Command name \'{0}\' is invalid'.format(cmd))
            return None
        
        if 'command' in self.mapref.keys():
            
            if not cmd in self.index.keys():
                return False
            
            del self.mapref['command'][self.index[cmd]]
        
        if len(self.mapref['command']) == 0:
            del self.mapref['command']
        
        self.sort_index()
        return True
    
    def sort_index(self):
        temp = self.index
        self.index = {}
        for name in temp:
            for key, binding in enumerate(self.mapref['command']):
                if name != binding.options['cmd'].lower():
                    continue
                self.index[name] = key
                continue
    
    def trigger(self, event, *args):
        """Trigger a command."""
        try:
            if not event.trigger.lower() in self.index.keys():
                self.debug('>> No such command as \'{0}\''.format(event.trigger))
                return None
        except AttributeError:
            self.debug('>> Invalid command provided')
            return None
        
        return self.run(self.mapref['command'][self.index[event.trigger.lower()]], event, *args)
    
    def run(self, binding, event, *args):
        """Attempt to run a command's event binding."""
        cmd = event.trigger.lower()
        
        for key, value in binding.options.items():
            
            if not value:
                continue
            
            if key == 'cmd' and value.lower() == cmd:
                continue
            
            if key == 'priv':
                if not self.privd(data.user, binding.level, data.trigger):
                    return None
                continue
            if key == 'channel':
                '''if dAmn.format_ns(str(option)).lower() == str(data.ns).lower():
                    continue
                return None'''
                continue
            
            try:
                # Process event item
                item = getattr(event, key)
            except AttributeError:
                return None
                
            
            # Try to match as a string
            try:
                if str(item).lower() == str(value).lower():
                    continue
            except Exception:
                pass
            # Are they the same type?
            if type(item) != type(value):
                return None
            
            # Do they hold the same value?
            if item == value:
                continue
            
            return None
        
        sub = event.arguments(1)
        if sub == '?':
            if binding.options and binding.options['help']:
                #dAmn.say(event.target, ': '.join([str(event.user), binding.options['help']]))
                return None
            
            #dAmn.say(data.target, event.user+': There is no information for this command.')
            return None
        
        '''if self.debug:
            self._write('** Running command \''+data.trigger+'\' for '+str(data.user)+'.')'''
        try:
            binding.call(event, *args)
        except Exception as e:
            log = self.debug
            log('>> Failed to execute command "{0}"!'.format(event.trigger))
            log('>> Error:')
            tb = traceback.format_exc().splitlines()
            for line in tb:
                log('>> {0}'.format(line))
        return None
    
    def privd(self, user, level, cmd):
        return True


# EOF

