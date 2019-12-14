
from .Input import Input
from phlibs.modules import Panfw

class PanfwInput(Input):
    """
    PanfwInput consumes an existing object, phlibs.modules.panfw, as it provides all the methods required.
    This is just a convienence class for readability more than anything.
    """
    def __init__(self,  mod_opts=None):
        super(PanfwInput, self).__init__()
        self.panfw = Panfw(mod_opts)

    def List(self):
        return self.panfw.List()