''' extensions.system module
    created by photofroggy
'''


from slate.extension import ExtensionBase


class Extension(ExtensionBase):
    
    def init(self, core):
        self.bind(self.join, 'command', cmd='join', priv='Operators')
        self.bind(self.part, 'command', cmd='part', priv='Operators')
        self.bind(self.refresh, 'command', cmd='refresh', priv='Owner')
        #self.bind(self.agent, 'command', cmd='agent', priv='Guests')
        #self.bind(self.quit, 'command', cmd='quit', priv='Owner')
        
    def join(self, cmd, dAmn):
        ns = self.clist(cmd, dAmn)
        t = dAmn.format_ns(cmd.target)
        
        if t.lower() != cmd.ns.lower():
            ns.append(t)
        
        if ns == []:
            print 'foo'
            dAmn.say(cmd.ns, '{0}: Use this command to make the bot join a channel.'.format(cmd.user))
            return
        
        for chan in ns:
            dAmn.join(chan)
    
    def part(self, cmd, dAmn):
        ns = self.clist(cmd, dAmn)
        if cmd.target.lower() != cmd.ns.lower():
            ns.append(cmd.target)
        
        if not ns:
            dAmn.part(cmd.ns)
            return
        
        for chan in ns:
            dAmn.part(chan)
    
    def refresh(self, cmd, dAmn):
        dAmn.say(cmd.ns, '{0}: Refreshing dAmn connection...'.format(cmd.user))
        dAmn.flag.disconnecting = True
        dAmn.disconnect()
        
    def clist(self, cmd, dAmn):
        chans = cmd.arguments(finish=True, sequence=True)
        
        try:
            chans.remove('')
        except ValueError:
            pass
        
        return [dAmn.format_ns(i) for i in chans]


# EOF
