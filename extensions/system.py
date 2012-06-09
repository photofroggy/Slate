''' extensions.system module
    created by photofroggy
'''


from slate.extension import ExtensionBase


class Extension(ExtensionBase):
    
    def init(self, core):
        self.bind(self.about, 'command', cmd='about')
        self.bind(self.agent, 'command', cmd='agent', priv='Guests')
        self.bind(self.commands, 'command', cmd='commands', priv='Guests')
        self.bind(self.quit, 'command', cmd='quit', priv='Owner')
        
    def about(self, cmd, dAmn):
        dAmn.say(cmd.ns, '{0}: Running Slate {1}.{2} {3} by p<b></b>hotofroggy. My owner is {4}.'.format(
            cmd.user,
            self.core.platform.version,
            self.core.platform.build,
            self.core.platform.state,
            self.core.config.owner
        ))
    
    def agent(self, cmd, dAmn):
        dAmn.say(cmd.ns, '{0}: <code>{1}</code>'.format(cmd.user, self.core.agent))
    
    def commands(self, cmd, dAmn):
        cmds = self.core.events.rules['command'].index.keys()
        cmds.sort()
        index = self.core.events.rules['command'].index
        available = []
        
        for name in cmds:
            obj = self.core.events.map['command'][index[name]]
            if self.core.users.has(cmd.user, obj.group):
                available.append(name)
        
        dAmn.say(cmd.ns, '{0}: Available commands: <code>{1}</code>'.format(cmd.user, ', '.join(available)))
    
    def quit(self, cmd, dAmn):
        dAmn.say(cmd.ns, '{0}: Shutting down...'.format(cmd.user))
        dAmn.flag.quitting = True
        dAmn.disconnect()


# EOF
