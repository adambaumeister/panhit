from .output import Output
from phlibs.modules import Panfw

class PanfwOutput(Output):
    """
    PanfwInput consumes an existing object, phlibs.modules.panfw, as it provides all the methods required.
    This is just a convienence class for readability more than anything.
    """
    def __init__(self,  mod_opts=None):


        self.panfw = Panfw(mod_opts)
        self.module_options = self.panfw.module_options
        self.module_options.remove_option("report_interval")

        super(PanfwOutput, self).__init__(mod_opts)
        self.pretty_name = "PANOS Device"
        self.image_small = "images/pan-logo-orange.png"

        self.image = "images/pan-logo-orange.png"
        self.type = "panfw"

    def Output(self, hl):
        return self.panfw.Output(hl)