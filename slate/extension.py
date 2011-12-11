''' slate.extension module
    created by photofroggy
'''


from reflex.base import Reactor


class ExtensionBase(Reactor):
    """ WOOOO """
    
    def init(self, core):
        sefl.core = core
        self.log = core.log



# EOF
