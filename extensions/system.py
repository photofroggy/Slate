''' extensions.system module
    created by photofroggy
'''


from slate.extension import ExtensionBase


class Extension(ExtensionBase):
    
    def init(self, core):
        self.bind(self.about, 'command', cmd='about')
        self.bind(self.agent, 'command', cmd='agent', priv='Guests')
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
    
    def quit(self, cmd, dAmn):
        dAmn.say(cmd.ns, '{0}: Shutting down...'.format(cmd.user))
        dAmn.flag.quitting = True
        dAmn.disconnect()


# EOF
