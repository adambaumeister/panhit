
from .Input import Input
from phlibs.modules import Panfw, ModuleOption

class PanfwInput(Input):
    """
    PanfwInput consumes an existing object, phlibs.modules.panfw, as it provides all the methods required.
    This is just a convienence class for readability more than anything.
    """
    def __init__(self,  mod_opts=None):
        self.panfw = Panfw(mod_opts)
        self.module_options = self.panfw.module_options
        self.module_options.remove_option("report_interval")

        xpath_option = ModuleOption('xpath')
        xpath_option.nice_name = "Xpath"
        xpath_option.help = "Xpath to address objects"

        self.module_options.add_opt(xpath_option)

        super(PanfwInput, self).__init__(mod_opts)
        self.pretty_name = "PANOS Device"
        self.image_small = "images/pan-logo-orange.png"

        self.image = "images/pan-logo-orange.png"
        self.type = "panfw"

        # Tags pulled from the firewall
        self.panos_tags = []


    def List(self):
        return self.panfw.List()