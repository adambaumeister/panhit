
from .Input import Input
from phlibs.modules import Panfw

class PanfwInput(Input):
    """
    PanfwInput consumes an existing object, phlibs.modules.panfw, as it provides all the methods required.
    This is just a convienence class for readability more than anything.
    """
    def __init__(self,  mod_opts=None):


        self.panfw = Panfw(mod_opts)
        self.module_options = self.panfw.module_options

        super(PanfwInput, self).__init__(mod_opts)
        self.pretty_name = "PANOS Device"
        self.image_small = "static/pan-logo-orange.png"
        self.image = "images/pan-logo-orange.png"


    def List(self):
        return self.panfw.List()