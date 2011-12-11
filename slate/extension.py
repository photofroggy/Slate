''' slate.extension module
    created by photofroggy
'''


from reflex.base import Reactor


class ExtensionBase(Reactor):
    """ WOOOO """
    
    def __init__(self, manager, core):
        self.core = core
        self.log = core.log
        super(ExtensionBase, self).__init__(manager, core)
        self.name = __file__.split('.')[1].replace('_', ' ')



# EOF
